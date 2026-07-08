-- Add community_status to segment leads by whether they have an active community
ALTER TABLE public.leads
ADD COLUMN IF NOT EXISTS community_status TEXT NOT NULL DEFAULT 'ACTIVE';
-- Values: 'ACTIVE' | 'PRE_LAUNCH' | 'NO_COMMUNITY'
