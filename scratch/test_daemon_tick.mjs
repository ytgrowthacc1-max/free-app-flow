import { createClient } from "@supabase/supabase-js";

console.log("Testing Supabase connectivity and settings...");
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);

const { data: leads, error } = await supabase
  .from("leads")
  .select("id, first_name, whop_username, completed, abandoned_message_sent, ai_bot_enabled")
  .limit(5);

console.log("Supabase leads query success:", !error, "Found leads:", leads?.length);
const { data: settings } = await supabase.from("settings").select("*");
console.log("Settings keys:", settings?.map(s => s.key));

console.log("Testing complete!");
process.exit(0);
