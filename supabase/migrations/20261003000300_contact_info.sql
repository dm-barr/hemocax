-- Datos de contacto del Banco de Sangre (dónde y cuándo donar), visibles para el donante.
insert into public.system_config(key,value,description) values
 ('contact_info',to_jsonb('Banco de Sangre del Hospital Regional Docente de Cajamarca (HRDC). Pregunta en el hospital la dirección y el horario de atención.'::text),'Dónde y cuándo donar: dirección, horario y teléfono que ve el donante')
on conflict(key) do nothing;

drop policy if exists config_read_public_keys on public.system_config;
create policy config_read_public_keys on public.system_config for select to authenticated
  using (key in ('donation_interval_days','male_interval_days','female_interval_days','male_annual_limit','female_annual_limit','result_recommendations','contact_info'));
