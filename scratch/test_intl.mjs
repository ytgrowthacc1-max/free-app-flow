function getCountryFlag(countryCode) {
  if (!countryCode || countryCode.length !== 2) return "🌐";
  const codePoints = countryCode
    .toUpperCase()
    .split("")
    .map((char) => 127397 + char.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}

function getCountryName(countryCode) {
  if (!countryCode) return "";
  try {
    const regionNames = new Intl.DisplayNames(["en"], { type: "region" });
    return regionNames.of(countryCode.toUpperCase()) || countryCode;
  } catch {
    return countryCode;
  }
}

console.log("US:", getCountryFlag("US"), getCountryName("US"));
console.log("IN:", getCountryFlag("IN"), getCountryName("IN"));
console.log("GB:", getCountryFlag("GB"), getCountryName("GB"));
console.log("BD:", getCountryFlag("BD"), getCountryName("BD"));
console.log("PH:", getCountryFlag("PH"), getCountryName("PH"));
console.log("DE:", getCountryFlag("DE"), getCountryName("DE"));
