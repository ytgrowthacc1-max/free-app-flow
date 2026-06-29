-- Add session_id column for anonymous lead tracking (Whop iframe)
ALTER TABLE leads ADD COLUMN IF NOT EXISTS session_id text;
CREATE INDEX IF NOT EXISTS leads_session_id_idx ON leads(session_id);
