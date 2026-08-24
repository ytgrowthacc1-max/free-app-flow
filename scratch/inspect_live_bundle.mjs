async function inspectLiveAdmin() {
  const res = await fetch("https://free-app-flow.vercel.app/assets/admin-Czwm19oK.js");
  console.log("Status:", res.status);
  const text = await res.text();
  console.log("Bundle snippet:", text.slice(0, 200));
}

inspectLiveAdmin();
