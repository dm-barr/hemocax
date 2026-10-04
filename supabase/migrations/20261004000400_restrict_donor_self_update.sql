-- Un donante solo puede cambiar, en su propia ficha, los datos de consentimiento de correo.
-- Motivo: la política «donors_update_own_consent» permite UPDATE de la fila propia y el permiso por columnas
-- (GRANT UPDATE (...)) no limita nada mientras exista el permiso de tabla completo que Supabase concede por defecto.
-- El personal (is_staff) y el servidor (service_role, sin auth.uid()) no se ven afectados.

create or replace function public.restrict_donor_self_update()
returns trigger language plpgsql security definer set search_path=public
as $$
declare permitidas text[] := array['consent_email','consent_at','consent_version','opted_out','preferred_channel','updated_at'];
begin
  if auth.uid() is null or public.is_staff() then return new; end if;
  if (to_jsonb(new) - permitidas) is distinct from (to_jsonb(old) - permitidas) then
    raise exception 'Solo puedes cambiar tu autorización de correos. Para corregir tus datos, habla con el Banco de Sangre.';
  end if;
  return new;
end $$;

drop trigger if exists donors_restrict_self_update on public.donors;
create trigger donors_restrict_self_update before update on public.donors
  for each row execute function public.restrict_donor_self_update();
