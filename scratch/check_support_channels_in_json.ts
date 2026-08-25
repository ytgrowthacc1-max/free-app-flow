import { supabaseAdmin } from "../src/lib/leads.server";

async function main() {
  const { data: rows } = await supabaseAdmin.from("leads").select("id, whop_user_id, scraped_data").not("whop_user_id", "is", null);
  
  let withChannel = 0;
  let missingChannel = 0;

  for (const r of rows ?? []) {
    const ch = (r.scraped_data as any)?.support_channel_id;
    if (ch) withChannel++;
    else missingChannel++;
  }

  console.log(`Leads with whop_user_id: ${rows?.length ?? 0}`);
  console.log(`With support_channel_id in scraped_data: ${withChannel}`);
  console.log(`Missing support_channel_id in scraped_data: ${missingChannel}`);
}

main().catch(console.error);
