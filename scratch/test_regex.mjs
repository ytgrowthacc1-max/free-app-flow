const sampleHtml = `<span style="font-family:var(--default-font-family)" data-accent-color="gray" class="fui-Text text-gray-10 fui-r-size-2">$2,719.35<!-- --> <!-- -->Earned</span>`;

const regex1 = /(\$[\d,]+(?:\.\d+)?)\s*(?:<!--\s*-->\s*)*Earned/i;
const match1 = sampleHtml.match(regex1);
console.log("Match 1 result:", match1 ? match1[1] : "NONE");

const regex2 = /(\$[\d,]+(?:\.\d+)?)\s*(?:<!--[\s\S]*?-->\s*)*Earned/i;
const match2 = sampleHtml.match(regex2);
console.log("Match 2 result:", match2 ? match2[1] : "NONE");
