# CLAUDE.md — Axon Support Site

**What it is:** the public support page for **Axon**, the iOS health-scores app (app repo: `github.com/jaygosalia4/Axon-Vital-Score`, private — local at `/Users/apple/Projects/VitalScore`). One static file, `index.html` (dark theme: four-score explainer, FAQ, contact `support@axon-app.com`). No build step, no dependencies.

**Where deployed:** GitHub Pages — **https://jaygosalia4.github.io/axon-support/** (this repo, source = `main` branch root, HTTPS enforced). App Store Connect's **Support URL** points here — keep it alive.

**How to update:** edit `index.html` → commit to `main` → `git push origin main`. Pages redeploys automatically in ~1 minute. Verify at the URL above.

**Rules:**
- This repo is **PUBLIC** (deliberately separate from the private app repo — see VitalScore `ENGINEERING.md`). Never put keys, emails dumps, or anything private here.
- Keep it a single self-contained `index.html` — no frameworks.

**Known issue (found 2026-07-12):** the "Privacy Policy" link points at `raw.githubusercontent.com/jaygosalia4/Axon-Vital-Score/main/PRIVACY_POLICY.md`, but that repo is private → the link 404s for users. Fix by hosting the policy on this public site (e.g. `privacy.html`) and relinking — coordinate with the v1.6.2 privacy-policy rewrite in the app repo.
