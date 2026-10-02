create extension if not exists pgcrypto;

create type public.app_role as enum ('ADMIN', 'STAFF', 'DONOR');
create type public.result_status as enum ('PENDING', 'AVAILABLE', 'NOTIFIED', 'CONSULTED', 'CRITICAL_PENDING');

create table public.donors (
  id bigint generated always as identity primary key,
  auth_user_id uuid unique references auth.users(id) on delete set null,
  dni text not null unique check (dni ~ '^[0-9]{8}$'),
  first_name text not null,
  last_name text not null,
  gender text not null check (gender in ('M','F')),
  birth_date date not null,
  phone text not null,
  email text,
  blood_type text check (blood_type in ('O','A','B','AB')),
  rh_factor text check (rh_factor in ('+','-')),
  status text not null default 'ACTIVE' check (status in ('ACTIVE','INACTIVE')),
  preferred_channel text not null default 'EMAIL' check (preferred_channel='EMAIL'),
  consent_email boolean not null default false,
  consent_at timestamptz,
  consent_version text,
  opted_out boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (consent_email = false or (consent_at is not null and consent_version is not null and email is not null)),
  constraint donors_blood_pair_check check ((blood_type is null) = (rh_factor is null))
);
create index donors_blood_group_idx on public.donors(blood_type,rh_factor);
create index donors_contactable_idx on public.donors(status,consent_email,opted_out);

create table public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  dni text not null unique check (dni ~ '^[0-9]{8}$'),
  full_name text not null,
  role public.app_role not null,
  can_release_results boolean not null default false,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  check (can_release_results = false or role in ('ADMIN','STAFF'))
);
create index profiles_dni_idx on public.profiles(dni);

create table public.donations (
  id bigint generated always as identity primary key,
  donor_id bigint not null references public.donors(id),
  donation_date date not null,
  donation_type text not null default 'WHOLE_BLOOD',
  notes text,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);
create index donations_donor_date_idx on public.donations(donor_id,donation_date desc);

-- Enforce the annual whole-blood cap in the database, including concurrent requests.
create or replace function public.enforce_annual_donation_limit()
returns trigger language plpgsql security definer set search_path=public
as $$
declare donor_gender text; annual_limit integer; existing_count integer; year_start date;
begin
  if new.donation_type <> 'WHOLE_BLOOD' then return new; end if;
  select gender into donor_gender from public.donors where id=new.donor_id for update;
  if donor_gender is null then raise exception 'Donante no encontrado'; end if;
  annual_limit := case donor_gender when 'M' then 4 when 'F' then 3 else 0 end;
  year_start := make_date(extract(year from new.donation_date)::integer,1,1);
  select count(*) into existing_count from public.donations
    where donor_id=new.donor_id and donation_type='WHOLE_BLOOD'
      and donation_date >= year_start and donation_date < (year_start + interval '1 year')::date;
  if existing_count >= annual_limit then
    raise exception 'Se alcanzó el máximo anual configurado para donaciones de sangre total (%)', annual_limit;
  end if;
  return new;
end $$;
create trigger donations_annual_limit before insert on public.donations
for each row execute function public.enforce_annual_donation_limit();

create table public.donation_results (
  id bigint generated always as identity primary key,
  donation_id bigint not null unique references public.donations(id),
  status public.result_status not null default 'PENDING',
  critical boolean not null default false,
  donor_message text,
  available_at timestamptz,
  released_by uuid references auth.users(id),
  notified_at timestamptz,
  consulted_at timestamptz,
  created_at timestamptz not null default now(),
  check (critical = false or status in ('PENDING','CRITICAL_PENDING')),
  check (status not in ('AVAILABLE','NOTIFIED','CONSULTED') or (critical=false and available_at is not null))
);

create table public.campaigns (
  id bigint generated always as identity primary key,
  name text not null,
  description text,
  location text,
  message_template text not null,
  blood_groups text[] not null default '{}',
  status text not null default 'DRAFT' check (status in ('DRAFT','ACTIVE','INACTIVE','CLOSED')),
  starts_at timestamptz,
  ends_at timestamptz,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);
create table public.communications (
  id bigint generated always as identity primary key,
  donor_id bigint not null references public.donors(id),
  campaign_id bigint references public.campaigns(id),
  result_id bigint references public.donation_results(id),
  related_donation_id bigint references public.donations(id),
  type text not null,
  channel text not null default 'EMAIL' check (channel='EMAIL'),
  email text not null,
  message text not null,
  status text not null check (status in ('PENDING','QUEUED','SENT','DELIVERED','READ','FAILED')),
  external_id text,
  error_message text,
  created_by uuid references auth.users(id),
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  created_year integer generated always as (extract(year from created_at at time zone 'UTC')::integer) stored
);
create index communications_donor_created_idx on public.communications(donor_id,created_at desc);
create index communications_type_created_idx on public.communications(type,created_at desc);
create unique index birthday_once_per_year_idx on public.communications(donor_id,created_year,type) where type='BIRTHDAY';
create unique index frequent_once_per_year_idx on public.communications(donor_id,created_year,type) where type='FREQUENT_DONOR';
create unique index donation_thanks_once_idx on public.communications(related_donation_id,type) where type='DONATION_THANKS' and related_donation_id is not null;
create unique index return_reminder_once_per_donation_idx on public.communications(related_donation_id,type) where type='RETURN_REMINDER' and related_donation_id is not null;

create table public.campaign_recipients (
  id bigint generated always as identity primary key,
  campaign_id bigint not null references public.campaigns(id),
  donor_id bigint not null references public.donors(id),
  communication_id bigint references public.communications(id),
  status text not null default 'PENDING',
  created_at timestamptz not null default now(),
  unique(campaign_id,donor_id)
);
create table public.notifications (
  id bigint generated always as identity primary key,
  donor_id bigint not null references public.donors(id),
  communication_id bigint references public.communications(id),
  title text not null,
  message text not null,
  read_at timestamptz,
  created_at timestamptz not null default now()
);
create table public.system_config (
  key text primary key,
  value jsonb not null,
  description text,
  updated_at timestamptz not null default now()
);
insert into public.system_config(key,value,description) values
 ('male_annual_limit','4','Límite anual acordado: hombres'),
 ('female_annual_limit','3','Límite anual acordado: mujeres'),
 ('donation_interval_days','90','Valor provisional pendiente de validación clínica'),
 ('recognition_at_annual_limit','true','Reconocer al alcanzar el límite anual configurado')
on conflict(key) do nothing;

create table public.audit_logs (
  id bigint generated always as identity primary key,
  actor_id uuid references auth.users(id),
  actor_dni text,
  action text not null,
  entity text not null,
  entity_id bigint,
  detail jsonb not null default '{}',
  created_at timestamptz not null default now()
);
create index audit_created_idx on public.audit_logs(created_at desc);

create or replace function public.current_role()
returns public.app_role language sql stable security definer set search_path=public set row_security=off
as $$ select role from public.profiles where user_id=auth.uid() and active=true $$;
create or replace function public.current_donor_id()
returns bigint language sql stable security definer set search_path=public set row_security=off
as $$ select id from public.donors where auth_user_id=auth.uid() $$;
create or replace function public.is_staff()
returns boolean language sql stable security definer set search_path=public set row_security=off
as $$ select coalesce(public.current_role() in ('ADMIN','STAFF'),false) $$;
create or replace function public.can_release_results()
returns boolean language sql stable security definer set search_path=public set row_security=off
as $$ select exists(select 1 from public.profiles where user_id=auth.uid() and active and can_release_results and role in ('ADMIN','STAFF')) $$;

alter table public.profiles enable row level security;
alter table public.donors enable row level security;
alter table public.donations enable row level security;
alter table public.donation_results enable row level security;
alter table public.campaigns enable row level security;
alter table public.communications enable row level security;
alter table public.campaign_recipients enable row level security;
alter table public.notifications enable row level security;
alter table public.system_config enable row level security;
alter table public.audit_logs enable row level security;

create policy profiles_read_self_or_admin on public.profiles for select to authenticated using (user_id=auth.uid() or public.current_role()='ADMIN');
create policy donors_read_self_or_staff on public.donors for select to authenticated using (auth_user_id=auth.uid() or public.is_staff());
create policy donors_insert_staff on public.donors for insert to authenticated with check (public.is_staff());
create policy donors_update_staff on public.donors for update to authenticated using (public.is_staff()) with check (public.is_staff());
create policy donors_update_own_consent on public.donors for update to authenticated using (auth_user_id=auth.uid()) with check (auth_user_id=auth.uid());
create policy donations_read_owner_or_staff on public.donations for select to authenticated using (public.is_staff() or donor_id=public.current_donor_id());
create policy donations_insert_staff on public.donations for insert to authenticated with check (public.is_staff());
create policy donations_update_staff on public.donations for update to authenticated using (public.is_staff()) with check (public.is_staff());
create policy results_read_released_owner_or_staff on public.donation_results for select to authenticated using (
  public.is_staff() or (critical=false and status in ('AVAILABLE','NOTIFIED','CONSULTED') and exists(select 1 from public.donations d where d.id=donation_id and d.donor_id=public.current_donor_id()))
);
create policy campaigns_read_active_or_staff on public.campaigns for select to authenticated using (public.is_staff() or status='ACTIVE');
create policy campaigns_write_staff on public.campaigns for all to authenticated using (public.is_staff()) with check (public.is_staff());
create policy communications_staff_only on public.communications for all to authenticated using (public.is_staff()) with check (public.is_staff());
create policy campaign_recipients_staff_only on public.campaign_recipients for all to authenticated using (public.is_staff()) with check (public.is_staff());
create policy notifications_read_own_or_staff on public.notifications for select to authenticated using (public.is_staff() or donor_id=public.current_donor_id());
create policy notifications_update_own on public.notifications for update to authenticated using (donor_id=public.current_donor_id()) with check (donor_id=public.current_donor_id());
create policy config_read_staff on public.system_config for select to authenticated using (public.is_staff());
create policy config_write_admin on public.system_config for all to authenticated using (public.current_role()='ADMIN') with check (public.current_role()='ADMIN');
create policy audit_read_admin on public.audit_logs for select to authenticated using (public.current_role()='ADMIN');

revoke update on public.donation_results from anon, authenticated;
grant select on public.donation_results to authenticated;
grant update(consent_email,consent_at,consent_version,opted_out,preferred_channel) on public.donors to authenticated;

create or replace function public.release_noncritical_result(p_result_id bigint,p_donor_message text)
returns public.donation_results language plpgsql security definer set search_path=public
as $$
declare result_row public.donation_results;
begin
  if not public.can_release_results() then raise exception 'No autorizado para liberar resultados'; end if;
  update public.donation_results
    set status='AVAILABLE', critical=false, donor_message=p_donor_message,
        available_at=now(), released_by=auth.uid()
    where id=p_result_id and status='PENDING' and critical=false
    returning * into result_row;
  if result_row.id is null then raise exception 'Resultado inexistente, crítico o ya liberado'; end if;
  insert into public.audit_logs(actor_id,action,entity,entity_id,detail)
    values(auth.uid(),'RESULT_RELEASED','donation_result',p_result_id,jsonb_build_object('critical',false));
  return result_row;
end;
$$;

create or replace function public.create_pending_result()
returns trigger language plpgsql security definer set search_path=public
as $$ begin insert into public.donation_results(donation_id,status) values(new.id,'PENDING'); return new; end $$;
create trigger donation_pending_result after insert on public.donations
for each row execute function public.create_pending_result();
