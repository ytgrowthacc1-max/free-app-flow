-- Make columns nullable for partial onboarding capture
ALTER TABLE public.leads ALTER COLUMN whop_url DROP NOT NULL;
ALTER TABLE public.leads ALTER COLUMN niche DROP NOT NULL;
ALTER TABLE public.leads ALTER COLUMN timeline DROP NOT NULL;
ALTER TABLE public.leads ALTER COLUMN first_name DROP NOT NULL;
ALTER TABLE public.leads ALTER COLUMN email DROP NOT NULL;

-- Add new Whop-specific columns
ALTER TABLE public.leads ADD COLUMN IF NOT EXISTS whop_user_id TEXT;
ALTER TABLE public.leads ADD COLUMN IF NOT EXISTS whop_username TEXT;
ALTER TABLE public.leads ADD COLUMN IF NOT EXISTS completed BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE public.leads ADD COLUMN IF NOT EXISTS abandoned_message_sent BOOLEAN NOT NULL DEFAULT false;
