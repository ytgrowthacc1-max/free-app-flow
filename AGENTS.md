# MANDATORY GIT ACCOUNT & DEPLOYMENT RULES

## CRITICAL AUTHOR IDENTITY REQUIREMENT
- **GitHub Username**: `ytgrowthacc1-max`
- **GitHub Email**: `ytgrowth.acc1@gmail.com`
- **GitHub Remote URL**: `https://github.com/ytgrowthacc1-max/free-app-flow.git`

**NEVER USE `hibridas117` OR ANY OTHER EMAIL/NAME FOR COMMITS OR PUSHES.**
Vercel deployment protection strictly validates commit author emails. Pushes with `hibridas117@users.noreply.github.com` will fail Vercel deployment checks.

Before every `git commit` or `git push`, ALWAYS verify and enforce:
```bash
git config user.email "ytgrowth.acc1@gmail.com"
git config user.name "ytgrowthacc1-max"
```

## MANDATORY WHOP USER LOCATION EXTRACTION RULES
1. **Public Profile Extraction**:
   - For any lead with a `whop_username`, fetch `https://whop.com/@${cleanUsername}/` (with `@` and trailing `/`).
   - Extract the rendered location from the DOM (`<span class="...fui-Text...">City, CC</span>` or regex `([A-Za-z\s.'-]+,\s*([A-Z]{2}))`).
   - Parse into 2-letter ISO country code (`country`) and city (`city`).
2. **5-Tier Location Resolution Pipeline**:
   - Tier 1: Vercel Edge Headers (`x-vercel-ip-country`, `x-vercel-ip-city`, `x-vercel-ip-timezone`).
   - Tier 2: Public Profile (`https://whop.com/@${username}/` via `getWhopProfileEarnings` / `resolveWhopLocation`).
   - Tier 3: Browser Timezone (`Intl.DateTimeFormat().resolvedOptions().timeZone`) converted via `TIMEZONE_TO_COUNTRY`.
   - Tier 4: Whop `/api/v1/people` cache (for store visitors).
   - Tier 5: Direct IP lookup fallback (`http://ip-api.com/json/${ip}`).
3. **Database Auto-Persistence**:
   - Always auto-persist resolved `country`, `city`, and `timezone` to the Supabase `leads` table on every user interaction, lead creation, and admin list view.

