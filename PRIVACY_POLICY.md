# Privacy Policy — Axon

*Last updated: July 10, 2026*

## Overview

Axon ("the app", "we", "us") is a health app for iPhone that reads Apple Health data to calculate your Sleep, Recovery, Strain, and Readiness scores. This policy describes exactly what stays on your device, what leaves it, and under what conditions.

**The short version:** your scores are computed entirely on your device. Your health data never leaves your phone unless you explicitly choose to share it. We collect anonymous usage analytics (which screens you use — never health values). We do not sell your data. Ever.

## 1. On your device (never leaves your phone by default)

- **Apple HealthKit data** we read: sleep analysis and stages, heart rate and heart rate variability (HRV), resting heart rate, respiratory rate, blood oxygen (SpO₂), wrist temperature, VO₂max, workouts, active energy, steps, walking metrics, time in daylight, and environmental sound levels.
- **All four daily scores and every sub-score** — computed and stored on-device.
- **Daily check-in answers** (mood, energy, stress, meditation minutes).
- **Journal entries** (never uploaded, anywhere, under any setting).
- Your profile settings (age, height, weight, activity level).

**All scoring calculations run entirely on your device.** We do not write any data to Apple Health, and HealthKit data is never used for advertising.

## 2. Always-on: account and anonymous usage analytics (no health values)

When you sign in with Apple, the following non-health data is synced to our backend (Supabase, hosted on AWS) and to our product-analytics service (PostHog, US Cloud):

- **Account profile:** your Apple sign-in identifier, and your email/display name if you chose to share them with Sign in with Apple, plus the app version.
- **Usage events:** which screens you view, which controls you use, session length, and device context (app version, OS version, device model, timezone). These events carry **no health values** — a check-in event records that you answered, never what you answered. This is an enforced engineering rule, not a preference.

We use this to understand which features are used and to fix problems. PostHog is configured without session recording and without autocapture.

## 3. Opt-in: anonymized health-data contribution (off by default)

In **Profile → Privacy** there is a toggle: **"Contribute anonymized health data."** It is **off by default**.

- When **off** (the default): no health metrics leave your phone. Full stop.
- When **on**: your daily metrics (scores, HRV, resting heart rate, sleep summary and stages, respiratory rate, SpO₂, wrist-temperature deviation, VO₂max, activity totals) and check-in values are uploaded under a **random contribution ID** generated on your device. This ID is not your Apple identifier, is not derived from it, and is never stored alongside it — contributed data cannot be linked back to your account or identity by us or anyone else.
- You can turn it off at any time; uploading stops immediately.

We use contributed data solely to improve Axon's scoring models.

## 4. Per-report: feedback diagnostics (off by default)

When you send in-app feedback, you can flip **"Attach diagnostic data"** for that report. If you do, the report includes your last 14 days of scores and recent app logs so we can debug your issue. This attachment is tied to your account (so we can reply to *your* problem) and is used only for handling that report. The toggle is off by default and applies to a single report at a time.

## 5. Account deletion — real and immediate

**Profile → Delete Account** permanently deletes, in one action:

- all local data on your device (scores, check-ins, journal, settings, sign-in state), and
- all server rows tied to your account — profile (including email), usage events, feedback, logs — and any contributed health data under your device's contribution ID.

Deletion is executed by a dedicated server-side function; it is not reversible. You can also email us (below) for deletion.

## 6. Third parties

| Service | What it receives | What it never receives |
|---|---|---|
| **Supabase** (supabase.com, on AWS) | Account profile, usage events, feedback, opt-in contributions, opt-in diagnostics | Health values outside the two opt-ins; journal entries |
| **PostHog** (posthog.com, US Cloud) | Anonymous usage events + device context, keyed by your Apple sign-in identifier | Any health value; your email or name; journal entries |

We do not sell, trade, or rent your personal information. We do not use your data for advertising. No other third parties receive your data.

## 7. Children's privacy

Axon is not directed at children under 13. We do not knowingly collect personal information from children.

## 8. Changes to this policy

We may update this policy periodically; material changes will be reflected by the date at the top. Continued use of the app after changes constitutes acceptance.

## Contact

For privacy questions or data deletion requests:

**Email:** support@axon-app.com
**GitHub:** https://github.com/jaygosalia4/Axon-Vital-Score

---

*Axon is built by an independent developer. Your health data stays yours — by default, it stays on your phone.*
