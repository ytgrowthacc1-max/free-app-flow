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
