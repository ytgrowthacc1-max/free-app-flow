-- Add willing_to_invest column to public.leads table
ALTER TABLE public.leads
ADD COLUMN IF NOT EXISTS willing_to_invest TEXT;
