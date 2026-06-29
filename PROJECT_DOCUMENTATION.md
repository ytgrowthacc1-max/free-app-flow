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

### Pushing to GitHub
All clean code is located in the `new-github-repo` folder, linked to the `ytgrowthacc1-max` GitHub account:
1. Ensure your local git config is correct:
   ```bash
   git config user.email "ytgrowth.acc1@gmail.com"
   git config user.name "ytgrowthacc1-max"
   ```
2. Commit and push your changes:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

### Syncing Environment Variables to Vercel
If you add or update keys in `.env`, run the sync script to update Vercel:
```bash
node scripts/set_vercel_envs.cjs
```

### Manual Vercel Deployments
To force a build from local workspace directly to production:
```bash
npx vercel --prod --yes
```

---

## 3. Whop OAuth & Email Capture Integration

The app captures lead emails via two methods:

### Method A: Standalone OAuth Flow (Verified Email)
1. User clicks **"Apply for a Free Build"** on `https://free-app-flow.vercel.app/`.
2. App directs them to Whop OAuth Authorize page with requested scopes:
   `email openid forum:post:create forum:read chat:read chat:message:create support_chat:read support_chat:message:create experience:create company:basic:read dms:read dms:message:manage`
3. Upon approval, Whop returns an authorization code.
4. Server function `exchangeOAuthCode` trades the code for an access token, then requests verified user data from the **OIDC user info endpoint**:
   `GET https://api.whop.com/oauth/userinfo`
5. The `sub`, `email`, and `preferred_username` are resolved and saved to the `leads` table.

### Method B: Iframe Auto-Capture (Zero Click)
1. If the app is opened inside the Whop user panel iframe, it detects `isInsideWhop: true` and attempts background lead registration.
2. In `registerAnonymousLead`, the app requests memberships from the API:
   `GET https://api.whop.com/api/v1/memberships`
3. **Dashboard Requirement:** You must enable `member:email:read` and `member:basic:read` permissions inside your **Whop Developer Dashboard** for the memberships lookup to return the email successfully.
4. If permissions are missing, it registers the lead's username and ID anonymously, then prompts them for their email in Step 8 of the onboarding funnel.

---

## 4. Supabase Database Configuration

*   **Current Active Project ID:** `thwsnpfoipeoowguhrbu` (linked to `hibridas` account).
*   **Local CLI Token:** `<your_supabase_token>`.
*   **Database Migrations:** Running migrations updates tables (e.g. `leads` with Whop ID, username, email, and session tracking columns).
