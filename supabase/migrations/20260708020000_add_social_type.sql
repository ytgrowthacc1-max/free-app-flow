-- Add social_type column to public.leads table
ALTER TABLE public.leads
ADD COLUMN IF NOT EXISTS social_type TEXT NOT NULL DEFAULT 'discord';
