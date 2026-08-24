# Project Documentation Handbook

This document outlines the architecture, deployment workflows, database schema, and integrations for the **App Builders / Free App Flow** project.

---

## 1. Project Structure & Key Files

This project is built using **TanStack Start** (a full-stack React framework with SSR and React Router) and styled with TailwindCSS/Vanilla CSS.

*   `src/routes/` - Contains the application views and routing hierarchy:
    *   `index.tsx` - The main user onboarding funnel (Steps 1–8). Features automated iframe check (`isInsideWhop`) and redirect hooks.
    *   `admin.tsx` - Admin panel dashboard displaying captured leads and lead details. Securely password-protected.
    *   `experiences.$id.tsx` - App showcase view.
*   `src/lib/` - Shared business logic and server functions:
    *   `leads.functions.ts` - Houses core API actions (e.g. `registerAnonymousLead`, `exchangeOAuthCode`, `getOAuthUrl`). It interfaces with Supabase and Whop.
    *   `leads.server.ts` - Supabase admin client initialization (using `service_role` key).
*   `src/integrations/` - Third-party API client utilities:
    *   `supabase/client.ts` - Client-side Supabase client.
    *   `supabase/types.ts` - Generated database TypeScript definitions.
*   `scripts/` - Maintenance and utility scripts:
    *   `set_vercel_envs.cjs` - Automatically parses `.env` and bulk uploads them to Vercel (Production/Preview/Development).
*   `supabase/` - Database schemas and configurations:
    *   `config.toml` - Supabase project links and CLI settings.
    *   `migrations/` - Database tables, indexes, and schema update history.

---

## 2. Deploy Workflows & Git Remote Rules

### 1. Primary GitHub Repository (`ytgrowthacc1-max`)
All code and deployments are linked to the **`ytgrowthacc1-max`** GitHub account (`ytgrowth.acc1@gmail.com`). 

*   **Repository URL**: `https://github.com/ytgrowthacc1-max/free-app-flow.git`
*   **Git Author Configuration**:
    ```bash
    git config user.email "ytgrowth.acc1@gmail.com"
    git config user.name "ytgrowthacc1-max"
    ```
*   **Authentication Token (Bypasses Prompts Forever)**:
    The remote is pre-configured with the GitHub Personal Access Token (PAT) so all automated agents and scripts can push directly via API without interactive prompts:
    ```bash
    git remote set-url origin https://<TOKEN>@github.com/ytgrowthacc1-max/free-app-flow.git
    ```

> [!CAUTION]
> **Never** commit or push using the `hibridas117` account. Vercel deployment permissions are strictly tied to `ytgrowthacc1-max` and will reject/block deployments from mismatched authors.

---

### 2. Automated Vercel Deployments

1. **Package Manager Assurance**:
   Ensure `"packageManager": "npm@10.8.2"` is in `package.json` and no leftover `bun.lock` file exists in the directory.
2. **Build and Deploy**:
   ```bash
   npx vercel build --prod --yes
   npx vercel deploy --prebuilt --prod --yes
   ```
   *(Or run `node scratch/deploy_vercel.mjs`)*.

---

## 3. Whop Location Tracking & Lead Count Architecture

### 1. Whop GeoIP & Billing Address Telemetry
*   **Resolver**: `src/lib/location.server.ts` resolves user locations by querying and caching Whop's `/api/v1/people` telemetry and `/api/v5/company/payments` billing data.
*   **Emoji Flags**: Dynamically formats ISO country codes into emoji flags (`US` -> 🇺🇸, `IN` -> 🇮🇳, `GB` -> 🇬🇧, `PH` -> 🇵🇭) and full country names.
*   **Dashboard & Notifications**:
    *   Table header: `Name / Location` with live country badges.
    *   Detail Drawer: Displays City, Country, Timezone (`America/Chicago`, `Asia/Calcutta`), and Device type.
    *   Telegram alerts: Automatically includes user location and timezone.

### 2. Lead Count Aggregation
*   **Avoid `.limit(500)` cap**: In `adminListLeads` (`src/lib/leads.functions.ts`), exact global statistics are calculated using `{ count: "exact" }` queries in parallel, ensuring the total leads count accurately reflects all database rows (**3,870+ leads**).

## 3. Whop OAuth & Email Capture Integration

The app captures lead emails via two distinct methods, optimized for different contexts:

### Method A: Standalone OAuth Flow (Verified Email)
1. **Trigger:** User clicks **"Apply for a Free Build"** on a standalone browser window (e.g. `https://free-app-flow.vercel.app/`).
2. **Authorize redirect:** App directs them to the Whop OAuth Authorize page with requested scopes:
   `email openid forum:post:create forum:read chat:read chat:message:create support_chat:read support_chat:message:create experience:create company:basic:read dms:read dms:message:manage`
3. **Authorization code:** Upon approval, Whop redirects back with an authorization code.
4. **Token exchange & Userinfo:** The server function `exchangeOAuthCode` trades the code for an access token and requests verified user data from the **OIDC user info endpoint**:
   `GET https://api.whop.com/oauth/userinfo`
5. **Database update:** The user's ID (`sub`), email, and username are resolved and written to the `leads` table.

### Method B: Iframe Auto-Capture & Email Enrichment (Zero-Click)
1. **Iframe detection:** If the app is loaded inside the Whop user panel frame, it detects `isInsideWhop: true` and automatically invokes the server-side registration flow.
2. **Identity verification:** The frontend requests the server to read and verify the `x-whop-user-token` header (automatically attached by Whop's reverse proxy to all requests).
3. **Email enrichment:** Because the iframe JWT is signed and verified but cannot call public user endpoints (returning 401 Unauthorized), the server uses the company's Developer API key (`WHOP_COMPANY_API_KEY`) to request the user's memberships.
4. **Membership Lookup:** It calls `GET https://api.whop.com/api/v2/memberships?user_id=<user_id>` with the company API key, which returns the user's email directly on the membership object.
5. **Funnel pre-fill:** The user's resolved name and email are sent back to the client and pre-filled in the final onboarding steps, requiring zero typing from the user.

---

## 4. Supabase Database Configuration

*   **Supabase Account:** `hibriads117@gmail.com` (Owner of the database/project).
*   **Current Active Project ID:** `thwsnpfoipeoowguhrbu`
*   **Programmatic SQL Migrations:** 
    *   A secure SQL execution helper `public.exec_sql(sql text)` is installed in the database.
    *   Execution is strictly restricted (`REVOKE` from `PUBLIC`, `anon`, and `authenticated` roles; `GRANT` only to `service_role`).
    *   This allows future database migrations to be performed programmatically by the development agent using the `SUPABASE_SERVICE_ROLE_KEY` (via the REST RPC interface) without requiring manual SQL console access or database password entry.
*   **Database Schema:** Contains the `leads` table tracking onboarding prospects, scraping details, session IDs, and `community_status` ('ACTIVE' | 'PRE_LAUNCH' | 'NO_COMMUNITY').

---

## 5. Blueprint: Whop Iframe Auto-Capture & Email Enrichment Tactics

This section provides a complete, reusable blueprint of the tactics implemented in this project, which can be adapted to any Whop app in the future.

### Tactic 1: Iframe Environment Detection
To check if the application is running inside a Whop experience iframe rather than a standalone tab:
```typescript
const isInsideWhop = typeof window !== "undefined" &&
  (window.location.hostname.endsWith(".apps.whop.com") ||
   window.location.pathname.startsWith("/experiences/") ||
   window !== window.top);
```

### Tactic 2: Server-Side JWT Claims & Verification
Whop attaches a header named `x-whop-user-token` to all requests inside the iframe. This header is a JWT signed by Whop. 
*   **Do not** call `https://api.whop.com/api/v1/users/me` with it as a Bearer token; this will return a **401 Unauthorized** error.
*   **Instead**, verify the token signature using the `@whop/sdk` library with your **Client ID / App ID** (`WHOP_APP_ID`), and decode the claims locally using a base64url parser:
```typescript
import { verifyUserToken } from "@whop/sdk/lib/verify-user-token";

// 1. Verify the signature (automatically reads request headers)
const appId = process.env.WHOP_APP_ID;
const result = await verifyUserToken(request.headers, { appId, dontThrow: true });

// result.userId will contain the Whop user ID (e.g., 'user_XXXXXXXX')

// 2. Decode the claims locally to inspect metadata
const userToken = request.headers.get("x-whop-user-token");
const payload = JSON.parse(Buffer.from(userToken.split(".")[1], "base64url").toString("utf8"));
const userId = payload.sub || payload.userId;
```

### Tactic 3: Email Resolution via Memberships API v2
Since the user token does not allow querying user emails directly, use your **Company API Key** (which must have the `member:email:read` scope enabled under the Whop developer dashboard) to fetch the user's membership details:
```typescript
const companyApiKey = process.env.WHOP_COMPANY_API_KEY;
const membershipsRes = await fetch(
  `https://api.whop.com/api/v2/memberships?user_id=${userId}`,
  {
    headers: { Authorization: `Bearer ${companyApiKey}` }
  }
);

if (membershipsRes.ok) {
  const data = await membershipsRes.json();
  const membership = data.data?.[0];
  const email = membership?.email; // Resolved!
}
```

### Tactic 4: Bypass Cache Storage Bugs (Database Sync Assurance)
When developers test onboarding funnels, they frequently delete rows in their test database to reset state. If the frontend blindly caches the `lead_id` in `sessionStorage` or `localStorage`, the client will attempt to update a deleted row, causing the onboarding flow to fail and crash on final submission.

*   **Tactic:** Inside the iframe, **never** assume the cached `leadId` exists. Always run the `registerAnonymousLead` function on page mount and on primary click actions.
*   **Behavior:** The server function performs a fast lookup in the database checking by `whop_user_id` OR `session_id`. If the row is missing (e.g. deleted), it silently re-creates the row and returns a valid, refreshed `leadId` back to the frontend.
```typescript
// Client-side Onboarding Page Mount
useEffect(() => {
  if (isInsideWhop) {
    // Always call register/retrieve to ensure database state is in sync
    registerAnonymousLead({ data: { session_id: sid } }).then((res) => {
      setLeadId(res.id);
      sessionStorage.setItem("lead_id", res.id);
    });
  }
}, [isInsideWhop]);
```

---

## 6. Payment Recovery & Failed Checkout Outreach Automation

The background daemon (`scripts/automation_daemon.ts`) continuously monitors Whop transactions for incomplete or failed payments and initiates proactive support outreach.

### Automation Workflow
1. **Polls Payments Endpoint:** `GET https://api.whop.com/api/v5/company/payments?per=50`
2. **Detection & Filtering:** Identifies payments where `status !== 'paid'`, `payments_failed > 0`, or `paid_at === null` with a 5-minute buffer delay so active checkouts are not interrupted.
3. **Failure Classification:**
   * **`failed_card`:** Card declined or transaction error (`payments_failed >= 1`).
   * **`incomplete_checkout`:** Abandoned session (e.g. Apple Pay session started but not finished).
4. **1-on-1 Support Channel:** Automatically opens a support channel via `POST https://api.whop.com/api/v1/support_channels` for `whop_user_id`.
5. **Contextual Support DM:** Sends a tailored, friendly question (e.g., *"hey {first_name}, noticed your payment for ${amount} had an issue going through. did your card get declined or did you run into any errors at checkout?"*).
6. **Persistent Deduplication:** Records the transaction in the Supabase `payment_recoveries` table and local cache (`.tmp/processed_payments.json`) to prevent duplicate outreach.

