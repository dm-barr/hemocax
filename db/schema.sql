-- Esquema de referencia del MVP. La demo actual persiste en JSON y aún no ejecuta este SQL.
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK (role IN ('ADMIN','STAFF','DONOR')),
  can_release_results BOOLEAN NOT NULL DEFAULT FALSE, active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS donors (
  id BIGSERIAL PRIMARY KEY, user_id BIGINT UNIQUE REFERENCES users(id), document_number TEXT UNIQUE NOT NULL,
  first_name TEXT NOT NULL, last_name TEXT NOT NULL, birth_date DATE NOT NULL, gender TEXT NOT NULL,
  phone TEXT NOT NULL, email TEXT, blood_type TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'ACTIVE',
  preferred_channel TEXT NOT NULL DEFAULT 'EMAIL', consent_email BOOLEAN NOT NULL DEFAULT FALSE,
  consent_at TIMESTAMPTZ, consent_version TEXT, opted_out BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS donors_blood_type_idx ON donors(blood_type);
CREATE INDEX IF NOT EXISTS donors_contact_consent_idx ON donors(consent_email,opted_out,status);
CREATE TABLE IF NOT EXISTS donations (
  id BIGSERIAL PRIMARY KEY, donor_id BIGINT NOT NULL REFERENCES donors(id), donation_date DATE NOT NULL,
  donation_type TEXT NOT NULL DEFAULT 'SANGRE_TOTAL', notes TEXT, created_by BIGINT REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS donations_donor_date_idx ON donations(donor_id,donation_date DESC);
CREATE TABLE IF NOT EXISTS donation_results (
  id BIGSERIAL PRIMARY KEY, donation_id BIGINT UNIQUE NOT NULL REFERENCES donations(id),
  status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING','AVAILABLE','NOTIFIED','CONSULTED','CRITICAL_PENDING')),
  critical BOOLEAN NOT NULL DEFAULT FALSE, summary TEXT, available_at TIMESTAMPTZ, released_by BIGINT REFERENCES users(id),
  notified_at TIMESTAMPTZ, consulted_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS campaigns (
  id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL, description TEXT, location TEXT, message_template TEXT NOT NULL,
  blood_types TEXT[] NOT NULL DEFAULT '{}', status TEXT NOT NULL DEFAULT 'DRAFT', starts_at TIMESTAMPTZ,
  ends_at TIMESTAMPTZ, created_by BIGINT REFERENCES users(id), created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS campaign_recipients (
  id BIGSERIAL PRIMARY KEY, campaign_id BIGINT NOT NULL REFERENCES campaigns(id), donor_id BIGINT NOT NULL REFERENCES donors(id),
  communication_id BIGINT, status TEXT NOT NULL DEFAULT 'PENDING', created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(campaign_id,donor_id)
);
CREATE TABLE IF NOT EXISTS communications (
  id BIGSERIAL PRIMARY KEY, donor_id BIGINT NOT NULL REFERENCES donors(id), campaign_id BIGINT REFERENCES campaigns(id),
  result_id BIGINT REFERENCES donation_results(id), type TEXT NOT NULL, channel TEXT NOT NULL DEFAULT 'EMAIL',
  related_donation_id BIGINT REFERENCES donations(id), email TEXT NOT NULL, message TEXT NOT NULL,
  status TEXT NOT NULL, external_id TEXT, error_message TEXT,
  created_by BIGINT REFERENCES users(id), sent_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS communications_donor_created_idx ON communications(donor_id,created_at DESC);
CREATE TABLE IF NOT EXISTS system_config (
  key TEXT PRIMARY KEY, value JSONB NOT NULL, description TEXT, updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
INSERT INTO system_config(key,value,description) VALUES
 ('male_annual_limit','4','Límite anual inicial definido por el Banco de Sangre'),
 ('female_annual_limit','3','Límite anual inicial definido por el Banco de Sangre'),
 ('donation_interval_days','90','Valor provisional; requiere validación institucional')
ON CONFLICT(key) DO NOTHING;
CREATE TABLE IF NOT EXISTS notifications (
  id BIGSERIAL PRIMARY KEY, donor_id BIGINT NOT NULL REFERENCES donors(id), communication_id BIGINT REFERENCES communications(id),
  title TEXT NOT NULL, message TEXT NOT NULL, read_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS audit_logs (
  id BIGSERIAL PRIMARY KEY, user_id BIGINT REFERENCES users(id), actor TEXT NOT NULL, action TEXT NOT NULL,
  entity TEXT NOT NULL, entity_id BIGINT, detail JSONB NOT NULL DEFAULT '{}', created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
