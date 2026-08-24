# Deployment, Git Remotes, and Location Tracking Directives

## 1. Git Repository & Identity Rules
- **Primary GitHub Account**: `ytgrowthacc1-max` (email: `ytgrowth.acc1@gmail.com`).
- **Primary Repository**: `https://github.com/ytgrowthacc1-max/free-app-flow.git`.
- **Authentication**: Uses an embedded GitHub Personal Access Token (PAT) configured in the git remote URL so that all agent git operations can push non-interactively without prompting.
- **Do NOT use `hibridas117`**: Pushes or commits with author `hibridas117` will be blocked by Vercel deployment permissions. Always ensure git config author is `ytgrowthacc1-max <ytgrowth.acc1@gmail.com>`.

---

## 2. Vercel Deployment Architecture
- **Vercel Project**: `free-app-flow` (`prj_MZ7D2E0OeSPFzFhBNgUDk4e1WGlX` under team `team_Z1tAMR0vomaO2L8Hi98tAFPI`).
- **Package Manager Rule**: Always use `npm` (defined as `"packageManager": "npm@10.8.2"` in `package.json`). Ensure NO `bun.lock` or `bunfig.toml` exists in the root workspace, which tricks Vercel CLI into attempting `bun install`.
- **Deploy Command**:
  To deploy directly from the agent or terminal without interactive prompts:
  1. Build: `npx vercel build --prod --yes`
  2. Deploy: `npx vercel deploy --prebuilt --prod --yes`
  *(Or execute `node scratch/deploy_vercel.mjs`)*.

---

## 3. Whop Location & Demographics Telemetry
- **API Endpoints**:
  - `GET https://api.whop.com/api/v1/people?company_id={company_id}`: GeoIP telemetry (`location.country`, `location.city`, `timezone`, `device`, `last_ip`).
  - `GET https://api.whop.com/api/v5/company/payments`: Verified credit card billing addresses (`billing_address.country`, `city`, `state`, `postal_code`).
- **Implementation**:
  - `src/lib/location.server.ts`: In-memory cached resolver with ISO country code to emoji flag conversion (`US` -> 🇺🇸, `IN` -> 🇮🇳, `GB` -> 🇬🇧, `PH` -> 🇵🇭) and full country names.
  - `adminListLeads`: Enriches leads on load and queries exact database counts via `{ count: "exact" }` (never hardcode `.limit(500)` for total counters).
  - `notifyTelegram`: Appends `Location: 🇺🇸 United States (New Caney, US) [America/Chicago]` to lead alerts.
