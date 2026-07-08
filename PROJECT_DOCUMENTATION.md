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

## 2. Deploy Workflows

### 1. Pushing to GitHub (new-github-repo)
All clean code is located in the `new-github-repo` folder, linked to the `ytgrowthacc1-max` GitHub account. 

#### Setup Token (Bypasses Prompts Forever)
To avoid any authentication popup or account selection, run this in the `new-github-repo` folder:
```bash
git remote set-url origin https://YOUR_TOKEN_HERE@github.com/ytgrowthacc1-max/free-app-flow.git
```

#### Push Commands
1. Ensure your local git config is correct:
   ```bash
   git config user.email "ytgrowth.acc1@gmail.com"
   git config user.name "ytgrowthacc1-max"
   ```
2. Commit and push:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

### 2. Syncing Environment Variables to Vercel
If you add or update keys in `.env`, run the sync script to update Vercel:
```bash
node scripts/set_vercel_envs.cjs
```

### 3. Manual Vercel Deployments
To force a build from local workspace directly to production:
1. **CRITICAL**: Stage and commit your changes in the root folder so the latest commit author is `ytgrowth.acc1@gmail.com`:
   ```bash
   git config user.email "ytgrowth.acc1@gmail.com"
   git config user.name "ytgrowthacc1-max"
   git add .
   git commit -m "Your commit message"
   ```
   *(If you don't commit, Vercel will match the author of the previous commit (e.g. hibridas117) and block the deployment)*
2. Run Vercel deploy:
   ```bash
   npx vercel --prod --yes
   ```

---

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
