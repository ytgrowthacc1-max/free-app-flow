import { calcLeadScore } from "../src/lib/leads.server.js";

const examples = [
  {
    name: "1. Verified UAE Creator with Profile Earnings ($100 Badge)",
    input: { memberCount: 150, monthlyPrice: 30, timeline: "Within a month", country: "AE", profileEarningsBadge: "$100", willingToInvest: "Yes" },
    expectedTag: "HOT",
  },
  {
    name: "2. High Earner UK Whop Owner ($10K+ Badge)",
    input: { memberCount: 600, monthlyPrice: 50, timeline: "ASAP / within 1 week", country: "GB", profileEarningsBadge: "$10K+ Earned", profileEarningsUsd: 12500, willingToInvest: "Yes" },
    expectedTag: "HOT",
  },
  {
    name: "3. Pre-Launch Germany Creator with Budget (No Community)",
    input: { memberCount: 0, monthlyPrice: 0, timeline: "ASAP / within 1 week", country: "DE", willingToInvest: "Yes" },
    expectedTag: "HOT",
  },
  {
    name: "4. Pre-Launch Germany Creator Refusing to Invest (Wants 100% Free Solution)",
    input: { memberCount: 0, monthlyPrice: 0, timeline: "ASAP / within 1 week", country: "DE", willingToInvest: "No, I need a 100% free solution" },
    expectedTag: "COLD",
  },
  {
    name: "5. USA Creator with Visible $0 Profile Earnings & Budget",
    input: { memberCount: 100, monthlyPrice: 30, timeline: "ASAP / within 1 week", country: "US", profileEarningsBadge: "$0", willingToInvest: "Yes" },
    expectedTag: "HOT",
  },
  {
    name: "6. Canada Creator with Low Urgency Timeline (2 months+)",
    input: { memberCount: 25, monthlyPrice: 20, timeline: "2 months+", country: "CA", willingToInvest: "No" },
    expectedTag: "COLD",
  },
  {
    name: "7. Verified Earner in Indonesia ($500 Badge, Budget Yes)",
    input: { memberCount: 50, monthlyPrice: 30, timeline: "Within a month", country: "ID", profileEarningsBadge: "$500", willingToInvest: "Yes" },
    expectedTag: "HOT",
  },
  {
    name: "8. India Lead claiming $15,000 MRR (Refusing to Invest)",
    input: { memberCount: 500, monthlyPrice: 30, timeline: "ASAP / within 1 week", country: "IN", willingToInvest: "No" },
    expectedTag: "COLD",
  },
  {
    name: "9. Pakistan Lead with Visible $0 Earnings & No Budget",
    input: { memberCount: 0, monthlyPrice: 0, timeline: "2 months+", country: "PK", profileEarningsBadge: "$0", willingToInvest: "No" },
    expectedTag: "COLD",
  },
  {
    name: "10. Default Form Input Filler (No Country, No Budget, Neutral Earnings)",
    input: { memberCount: 100, monthlyPrice: 10, timeline: "Within a month", country: null, willingToInvest: "No" },
    expectedTag: "COLD",
  },
];

console.log("=========================================================");
console.log("       UPDATED LEAD VALUATION SYSTEM EVALUATION           ");
console.log("=========================================================\n");

for (const item of examples) {
  const result = calcLeadScore(item.input);
  console.log(`📌 ${item.name}`);
  console.log(`   Inputs: Country=${item.input.country || "Unknown"}, Earnings=${item.input.profileEarningsBadge || "None"}, Timeline=${item.input.timeline}, Invest=${item.input.willingToInvest || "None"}`);
  console.log(`   Result: Score = ${result.score}/100 | Tag = ${result.tag} (Expected: ${item.expectedTag})`);
  console.log("---------------------------------------------------------");
}
