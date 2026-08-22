CREATE TABLE IF NOT EXISTS public.payment_recoveries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_id text UNIQUE NOT NULL,
  whop_user_id text NOT NULL,
  whop_username text,
  email text,
  amount numeric,
  currency text,
  failure_mode text,
  status text,
  channel_id text,
  message_sent boolean DEFAULT false,
  message_content text,
  created_at timestamptz DEFAULT now(),
  notified_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_payment_recoveries_payment_id ON public.payment_recoveries(payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_recoveries_user_id ON public.payment_recoveries(whop_user_id);
