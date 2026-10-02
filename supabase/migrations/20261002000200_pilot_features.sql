-- Funciones del piloto: resultados críticos, consentimiento versionado e historial,
-- bitácora automática, parámetros, plantillas aprobables, campañas informativas y derechos ARCO.

-- 1. Resultados críticos: el personal puede marcarlos; solo quien libera resultados puede quitar la marca.
create or replace function public.mark_result_critical(p_result_id bigint)
returns public.donation_results language plpgsql security definer set search_path=public
as $$
declare r public.donation_results;
begin
  if not public.is_staff() then raise exception 'No autorizado'; end if;
  update public.donation_results set critical=true, status='CRITICAL_PENDING', donor_message=null
    where id=p_result_id and status='PENDING' returning * into r;
  if r.id is null then raise exception 'Resultado inexistente o ya liberado'; end if;
  insert into public.audit_logs(actor_id,actor_dni,action,entity,entity_id,detail)
    values(auth.uid(),(select dni from public.profiles where user_id=auth.uid()),'RESULT_MARKED_CRITICAL','donation_result',p_result_id,'{}'::jsonb);
  return r;
end $$;

create or replace function public.clear_result_critical(p_result_id bigint)
returns public.donation_results language plpgsql security definer set search_path=public
as $$
declare r public.donation_results;
begin
  if not public.can_release_results() then raise exception 'No autorizado'; end if;
  update public.donation_results set critical=false, status='PENDING'
    where id=p_result_id and status='CRITICAL_PENDING' returning * into r;
  if r.id is null then raise exception 'El resultado no está marcado como crítico'; end if;
  insert into public.audit_logs(actor_id,actor_dni,action,entity,entity_id,detail)
    values(auth.uid(),(select dni from public.profiles where user_id=auth.uid()),'RESULT_CRITICAL_CLEARED','donation_result',p_result_id,'{}'::jsonb);
  return r;
end $$;

-- 2. Parámetros: intervalos por sexo y recomendaciones posteriores al resultado.
insert into public.system_config(key,value,description) values
 ('male_interval_days',(select value from public.system_config where key='donation_interval_days'),'Días mínimos entre donaciones: hombres (provisional, validar con el médico)'),
 ('female_interval_days',(select value from public.system_config where key='donation_interval_days'),'Días mínimos entre donaciones: mujeres (provisional, validar con el médico)'),
 ('result_recommendations',to_jsonb('Después de donar: hidrátate bien, evita esfuerzos físicos intensos durante 24 horas y mantén una alimentación equilibrada. Si presentas algún malestar, comunícate con el Banco de Sangre.'::text),'Recomendaciones que ve el donante junto a su resultado (validar con la Jefatura)')
on conflict(key) do nothing;

create policy config_read_public_keys on public.system_config for select to authenticated
  using (key in ('donation_interval_days','male_interval_days','female_interval_days','male_annual_limit','female_annual_limit','result_recommendations'));

-- 3. Consentimiento informado versionado e historial de cambios.
create table public.consent_versions (
  version text primary key,
  body text not null,
  active boolean not null default false,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);
alter table public.consent_versions enable row level security;
create policy consent_versions_read on public.consent_versions for select to authenticated using (true);
insert into public.consent_versions(version,body,active) values
 ('piloto-v1','Autorizo de forma libre, previa, expresa e informada al Banco de Sangre del Hospital Regional Docente de Cajamarca (HRDC), titular del tratamiento, a tratar mis datos personales (nombre, DNI, datos de contacto, grupo sanguíneo e historial de donaciones) para contactarme por correo electrónico con recordatorios de donación, agradecimientos, saludos, campañas y avisos de disponibilidad de resultados no críticos, conforme a la Ley N.° 29733 y su reglamento. No recibiré resultados críticos por este medio. Puedo revocar mi autorización en cualquier momento desde mi portal o solicitándolo al Banco de Sangre, y ejercer mis derechos de acceso, rectificación, cancelación y oposición.',true);

create or replace function public.publish_consent_version(p_body text)
returns text language plpgsql security definer set search_path=public
as $$
declare v text;
begin
  if public.current_role() is distinct from 'ADMIN' then raise exception 'Solo el administrador puede publicar el consentimiento'; end if;
  if length(trim(coalesce(p_body,''))) < 40 then raise exception 'El texto del consentimiento es demasiado corto'; end if;
  v := 'v' || ((select count(*) from public.consent_versions) + 1);
  update public.consent_versions set active=false where active;
  insert into public.consent_versions(version,body,active,created_by) values (v,trim(p_body),true,auth.uid());
  insert into public.audit_logs(actor_id,actor_dni,action,entity,detail)
    values(auth.uid(),(select dni from public.profiles where user_id=auth.uid()),'CONSENT_TEXT_PUBLISHED','consent_version',jsonb_build_object('version',v));
  return v;
end $$;

create table public.consent_events (
  id bigint generated always as identity primary key,
  donor_id bigint not null references public.donors(id) on delete cascade,
  action text not null check (action in ('GRANTED','REVOKED')),
  version text,
  recorded_by uuid,
  recorded_via text not null check (recorded_via in ('DONOR','STAFF','SISTEMA')),
  created_at timestamptz not null default now()
);
create index consent_events_donor_idx on public.consent_events(donor_id,created_at desc);
alter table public.consent_events enable row level security;
create policy consent_events_read on public.consent_events for select to authenticated
  using (public.is_staff() or donor_id=public.current_donor_id());

create or replace function public.log_consent_change()
returns trigger language plpgsql security definer set search_path=public
as $$
declare via text;
begin
  if tg_op='INSERT' and not new.consent_email then return new; end if;
  if tg_op='UPDATE' and new.consent_email is not distinct from old.consent_email and new.opted_out is not distinct from old.opted_out then return new; end if;
  via := case when auth.uid() is null then 'SISTEMA' when auth.uid()=new.auth_user_id then 'DONOR' else 'STAFF' end;
  insert into public.consent_events(donor_id,action,version,recorded_by,recorded_via)
    values(new.id, case when new.consent_email and not new.opted_out then 'GRANTED' else 'REVOKED' end, new.consent_version, auth.uid(), via);
  return new;
end $$;
create trigger donors_consent_log after insert or update on public.donors
  for each row execute function public.log_consent_change();

-- 4. Bitácora automática de cambios (solo nombres de campos modificados, no sus valores).
create or replace function public.audit_row_change()
returns trigger language plpgsql security definer set search_path=public
as $$
declare rowj jsonb; v_fields text[]; v_action text;
begin
  rowj := to_jsonb(case when tg_op='DELETE' then old else new end);
  if tg_op='INSERT' then v_action := tg_argv[0]||'_CREATED';
  elsif tg_op='UPDATE' then
    v_action := tg_argv[0]||'_UPDATED';
    v_fields := array(select n.key from jsonb_each(to_jsonb(new)) n join jsonb_each(to_jsonb(old)) o on o.key=n.key
                      where n.value is distinct from o.value and n.key not in ('updated_at'));
    if coalesce(array_length(v_fields,1),0)=0 then return new; end if;
  else v_action := tg_argv[0]||'_DELETED';
  end if;
  insert into public.audit_logs(actor_id,actor_dni,action,entity,entity_id,detail)
    values(auth.uid(),(select dni from public.profiles where user_id=auth.uid()),v_action,tg_argv[1],
           nullif(rowj->>'id','')::bigint,
           jsonb_strip_nulls(jsonb_build_object('campos',v_fields,'clave',coalesce(rowj->>'key',rowj->>'type',rowj->>'version'))));
  if tg_op='DELETE' then return old; end if;
  return new;
end $$;
create trigger donors_audit after insert or update or delete on public.donors for each row execute function public.audit_row_change('DONOR','donor');
create trigger donations_audit after insert or update or delete on public.donations for each row execute function public.audit_row_change('DONATION','donation');
create trigger campaigns_audit after insert or update or delete on public.campaigns for each row execute function public.audit_row_change('CAMPAIGN','campaign');
create trigger system_config_audit after insert or update or delete on public.system_config for each row execute function public.audit_row_change('CONFIG','config');

-- 5. Plantillas de mensajes automáticos con aprobación de la Jefatura.
create table public.message_templates (
  type text primary key check (type in ('BIRTHDAY','RETURN_REMINDER','DONATION_THANKS','FREQUENT_DONOR')),
  subject text not null,
  body text not null,
  approved boolean not null default false,
  approved_by text,
  approved_at timestamptz,
  updated_at timestamptz not null default now()
);
alter table public.message_templates enable row level security;
create policy message_templates_read_staff on public.message_templates for select to authenticated using (public.is_staff());
create policy message_templates_write_admin on public.message_templates for all to authenticated
  using (public.current_role()='ADMIN') with check (public.current_role()='ADMIN');
insert into public.message_templates(type,subject,body) values
 ('BIRTHDAY','¡Feliz cumpleaños de parte de HEMOCAX!','Feliz cumpleaños, {{nombre}}. Desde HEMOCAX y el Banco de Sangre te deseamos un excelente día. Gracias por formar parte de nuestra comunidad de donantes.'),
 ('RETURN_REMINDER','Ya puedes volver a donar sangre','Hola {{nombre}}. Según el intervalo registrado desde tu última donación, puedes volver a considerar participar como donante. La evaluación final corresponde al personal de salud.'),
 ('DONATION_THANKS','Gracias por tu donación de sangre','Hola {{nombre}}. Gracias por tu donación voluntaria. Cuídate y sigue las recomendaciones que te brindó el personal de salud.'),
 ('FREQUENT_DONOR','Reconocimiento a tu compromiso como donante','Hola {{nombre}}. Gracias por tu compromiso y tus donaciones de este año. Tu solidaridad es muy valiosa para la comunidad.');

create or replace function public.reset_template_approval()
returns trigger language plpgsql as $$
begin
  if new.body is distinct from old.body or new.subject is distinct from old.subject then
    new.approved := false; new.approved_by := null; new.approved_at := null; new.updated_at := now();
  end if;
  return new;
end $$;
create trigger message_templates_reset before update on public.message_templates for each row execute function public.reset_template_approval();
create trigger message_templates_audit after update on public.message_templates for each row execute function public.audit_row_change('TEMPLATE','template');

-- 6. Responsable de cada envío y campañas informativas.
alter table public.communications add column created_by_name text;
alter table public.campaigns add column kind text not null default 'CAMPAIGN' check (kind in ('CAMPAIGN','INFO'));

-- 7. Derechos ARCO: anonimizar a un donante (solo administrador). La cuenta de acceso se elimina desde el servidor.
create or replace function public.anonymize_donor(p_donor_id bigint)
returns void language plpgsql security definer set search_path=public
as $$
begin
  if public.current_role() is distinct from 'ADMIN' then raise exception 'Solo el administrador puede anonimizar datos'; end if;
  update public.donors set
    first_name='Donante', last_name='anonimizado', dni='9'||lpad(id::text,7,'0'), phone='000000000', email=null,
    birth_date=make_date(extract(year from birth_date)::integer,1,1), status='INACTIVE',
    consent_email=false, opted_out=true, auth_user_id=null
  where id=p_donor_id;
  if not found then raise exception 'Donante no encontrado'; end if;
  update public.communications set email='anonimizado', message='[eliminado]' where donor_id=p_donor_id;
  delete from public.notifications where donor_id=p_donor_id;
  insert into public.audit_logs(actor_id,actor_dni,action,entity,entity_id,detail)
    values(auth.uid(),(select dni from public.profiles where user_id=auth.uid()),'DONOR_ANONYMIZED','donor',p_donor_id,'{}'::jsonb);
end $$;

revoke execute on function public.mark_result_critical(bigint), public.clear_result_critical(bigint),
  public.publish_consent_version(text), public.anonymize_donor(bigint) from public, anon;
grant execute on function public.mark_result_critical(bigint), public.clear_result_critical(bigint),
  public.publish_consent_version(text), public.anonymize_donor(bigint) to authenticated;
