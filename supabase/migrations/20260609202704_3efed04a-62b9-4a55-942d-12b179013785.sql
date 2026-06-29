CREATE TABLE public.leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  whop_url TEXT NOT NULL,
  niche TEXT NOT NULL,
  member_count INTEGER,
  monthly_price INTEGER,
  mrr INTEGER DEFAULT 0,
  pain_point TEXT DEFAULT '',
  ideal_app TEXT DEFAULT '',
  timeline TEXT NOT NULL,
  first_name TEXT NOT NULL,
  email TEXT NOT NULL,
  social_handle TEXT DEFAULT '',
  lead_score INTEGER DEFAULT 0,
  lead_tag TEXT DEFAULT 'COLD',
  scrape_status TEXT DEFAULT 'Pending',
  ai_plan JSONB,
  scraped_data JSONB,
  selected_concept_index INTEGER,
  reserved_at TIMESTAMPTZ,
  claim_action TEXT
);

GRANT ALL ON public.leads TO service_role;

ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;

CREATE INDEX leads_created_at_idx ON public.leads (created_at DESC);
CREATE INDEX leads_tag_idx ON public.leads (lead_tag);