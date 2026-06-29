REVOKE ALL ON public.leads FROM anon, authenticated;
GRANT ALL ON public.leads TO service_role;

DROP POLICY IF EXISTS "Deny all client access to leads" ON public.leads;
CREATE POLICY "Deny all client access to leads"
  ON public.leads
  AS RESTRICTIVE
  FOR ALL
  TO anon, authenticated
  USING (false)
  WITH CHECK (false);