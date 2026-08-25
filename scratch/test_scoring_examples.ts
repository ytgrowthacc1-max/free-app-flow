import { calcLeadScore } from "../src/lib/leads.server.js";

const examples = [
  {
    name: "1. Verified UAE Creator with Profile Earnings ($100 Badge)",
    input: { memberCount: 150, monthlyPrice: 30, timeline: "Within a month", country: "AE", profileEarningsBadge: "$100" },
    expectedTag: "HOT",
  },
  {
    name: "2. High Earner UK Whop Owner ($10K+ Badge)",
    input: { memberCount: 600, monthlyPrice: 50, timeline: "ASAP / within 1 week", country: "GB", profileEarningsBadge: "$10K+ Earned", profileEarningsUsd: 12500 },
    expectedTag: "HOT",
  },
  {
    name: "3. Tier 1 USA Creator (No Public Earnings Badge, Moderate MRR)",
    input: { memberCount: 100, monthlyPrice: 30, timeline: "ASAP / within 1 week", country: "US" },
    expectedTag: "HOT",
  },
  {
    name: "4. Tier 1 Canada Creator (Small Community, No Earnings)",
    input: { memberCount: 25, monthlyPrice: 20, timeline: "ASAP / within 1 week", country: "CA" },
    expectedTag: "WARM",
  },
  {
    name: "5. High-Earnings Creator ($50K+ Badge), Unknown Country",
    input: { memberCount: 50, monthlyPrice: 20, timeline: "Within a month", country: null, profileEarningsBadge: "$50K+ Earned" },
    expectedTag: "HOT",
  },
  {
    name: "6. Verified Small Earner in Indonesia ($500 Badge)",
    input: { memberCount: 50, monthlyPrice: 30, timeline: "Within a month", country: "ID", profileEarningsBadge: "$500" },
    expectedTag: "WARM",
  },
  {
    name: "7. India Lead claiming $15,000 MRR (No Earnings Badge)",
    input: { memberCount: 500, monthlyPrice: 30, timeline: "ASAP / within 1 week", country: "IN" },
    expectedTag: "COLD",
  },
  {
    name: "8. Pakistan Lead with $0 MRR & No Community",
    input: { memberCount: 0, monthlyPrice: 0, timeline: "Someday", country: "PK" },
    expectedTag: "COLD",
  },
  {
    name: "9. Unknown Country, Default Form Inputs ($1,000 MRR, 100 members)",
    input: { memberCount: 100, monthlyPrice: 10, timeline: "Within a month", country: null },
    expectedTag: "COLD",
  },
  {
    name: "10. Germany Pre-Launch Creator ($0 MRR, Tier 1 Country)",
    input: { memberCount: 0, monthlyPrice: 0, timeline: "ASAP / within 1 week", country: "DE" },
    expectedTag: "WARM",
  },
];

console.log("=========================================================");
console.log("       PROPOSED LEAD VALUATION SYSTEM SCORING EXAMPLES     ");
console.log("=========================================================\n");

for (const item of examples) {
  const result = calcLeadScore(item.input);
  console.log(`📌 ${item.name}`);
  console.log(`   Inputs: Country=${item.input.country || "Unknown"}, Earnings=${item.input.profileEarningsBadge || "None"}, Members=${item.input.memberCount}, Timeline=${item.input.timeline}`);
  console.log(`   Result: Score = ${result.score}/100 | Tag = ${result.tag} (Expected: ${item.expectedTag})`);
  console.log("---------------------------------------------------------");
}
