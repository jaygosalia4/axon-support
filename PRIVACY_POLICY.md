# Privacy Policy — Axon

*Last updated: October 11, 2026*

## Overview

Axon ("the app", "we", "us") is a health app for iPhone that reads Apple Health data to calculate your Sleep, Recovery, Strain, and Readiness scores. This policy describes exactly what stays on your device, what leaves it, and under what conditions.

**The short version:** your scores are computed entirely on your device. Your health data never leaves your phone unless you explicitly choose to share it. We collect anonymous usage analytics (which screens you use — never health values). We do not sell your data. Ever.

## 1. On your device (never leaves your phone by default)

- **Apple HealthKit data** we read: sleep analysis and stages, heart rate and heart rate variability (HRV), resting heart rate, respiratory rate, blood oxygen (SpO₂), wrist temperature, VO₂max, workouts, active energy, steps, walking metrics, time in daylight, and environmental sound levels.
- **Dietary data from Apple Health** — calories, protein, carbohydrates, fat, fibre and caffeine — read **only if you ask us to**, from the Food tab. Axon does not request access to this data unless you tap that row, and it lets meals you log in another app (one that writes to Apple Health) appear in Axon without re-typing them. These values are read, shown on the Food tab, and nothing else: they are never uploaded, never included in the optional anonymized contribution below, and never sent to our analytics. **Axon writes nothing back to Apple Health**, so your entries in other apps are never changed.
- **Your calendar — times and counts only, and only if you turn it on** (Profile → Connections → Calendar). Axon asks for calendar access only when you tap that row. It then keeps, for each day, how many events you had, how many were meetings and how long they lasted, when the first started and the last ended, and whether an event ran past 20:00 or started before 08:00 — so it can show your week beside your scores. **Event titles, locations, notes and the people in them are never stored.** These day summaries stay on this iPhone: they are never uploaded, never included in the optional anonymized contribution below or in anything an AI assistant can read, and never sent to our analytics (which record only whether calendar access is on, never what your calendar holds). Turning it off in Axon deletes the stored days; you can also withdraw access in Settings → Privacy & Security → Calendars.
- **All four daily scores and every sub-score** — computed and stored on-device.
- **Daily check-in answers** (mood, energy, stress, meditation minutes).
- **Journal entries** (never uploaded, anywhere, under any setting).
- Your profile settings (age, height, weight, activity level).

**All scoring calculations run entirely on your device.** We do not write any data to Apple Health, and HealthKit data is never used for advertising.

## 2. Always-on: usage analytics (no health values), and the optional account

**Axon works without an account.** From v1.9.1, nothing about the app's core function — reading Apple Health and computing your four scores on your phone — requires you to sign in. Sign in with Apple is optional and lives in Profile → Account; it adds an invite code you can share and a way to send feedback that can be answered. It does not back up, sync or restore your health history — your scores, logs and settings live only on this phone (Apple Health is untouched, and the last 120 days of scores rebuild from it on a fresh install).

**From every install, whether or not you sign in**, the following non-health data goes to our product-analytics service (PostHog, US Cloud):

- **Usage events:** which screens you view, which controls you use, session length, and device context (app version, OS version, device model, timezone). These events carry **no health values** — a check-in event records that you answered, never what you answered. This is an enforced engineering rule, not a preference.
- **Install-level events:** that the app was opened for the first time, whether you were shown the sign-in option and from where, whether you tapped Sign in with Apple and the outcome (signed in / cancelled / did not complete — never the reason text), and once a day whether the app is being used anonymously or signed in.

While you are not signed in, these events are keyed by an anonymous identifier generated on your device by the analytics SDK — no account, no name, no email. The same non-health usage events are also written to our backend (Supabase, hosted on AWS) under a separate **random per-install identifier** generated on your device. That identifier is written only to records that carry no account and is never stored alongside your Apple identifier; those records carry no health values, no device context and no session identifier — only the event, the app version it came from, and that identifier. We use this to understand how many people who download the app reach their first score, and how many choose to sign in.

**When you sign in with Apple**, the following is added:

- **Account profile:** your Apple sign-in identifier, and your email/display name if you chose to share them with Sign in with Apple, plus the app version — synced to our backend.
- **Usage events** from that point are keyed by your Apple sign-in identifier in both systems (PostHog links the anonymous events on this device to that identity, as its identity model does; nothing is re-keyed on our backend, and the anonymous per-install records stay anonymous).

We use this to understand which features are used and to fix problems. PostHog is configured without session recording and without autocapture.

## 3. Opt-in: anonymized health-data contribution (off by default)

In **Profile → Privacy** there is a toggle: **"Contribute anonymized health data."** It is **off by default**.

- When **off** (the default): no health metrics leave your phone. Full stop.
- When **on**: your daily metrics (scores, HRV, resting heart rate, sleep summary and stages, respiratory rate, SpO₂, wrist-temperature deviation, VO₂max, activity totals) and check-in values are uploaded under a **random contribution ID** generated on your device. This ID is not your Apple identifier, is not derived from it, and is never stored alongside it — contributed data cannot be linked back to your account or identity by us or anyone else.
- You can turn it off at any time; uploading stops immediately.

We use contributed data solely to improve Axon's scoring models.

## 3a. Opt-in: Connect Axon to my AI assistant (off by default)

In **Profile → Connections** there is a switch: **"Connect Axon to my AI assistant."** It is **off by default**, and nothing in this section happens while it is off. It lets an AI assistant you choose (for example Claude or ChatGPT) read your Axon record and, if you allow it, log entries for you.

- **What leaves your phone when you turn it on:** what Axon shows you, worked out on your phone from the Apple Health data and your own entries listed in section 1 — as daily summaries and the app's own results, never the raw samples. In full:
  - **Scores:** the four daily scores, every sub-score, and the text of each breakdown row the app shows (the reading, its verdict, and the note that explains a missing or partial value), plus which scores are still building a baseline.
  - **Sleep:** time asleep, efficiency, deep / REM / core / awake time, time in bed, bed and wake times, whether the night was entered by hand, naps (including ones you logged), and the night's stage-by-stage timeline.
  - **Heart, recovery and training:** HRV and resting heart rate with their 30-day baselines, overnight resting heart rate, workouts (minutes, calories, count, average workout heart rate) and training load (daily stress, fatigue, fitness, form).
  - **The other readings in section 1, as daily values:** respiratory rate (and its 30-day baseline), blood oxygen (SpO₂, including how many low readings), wrist-temperature deviation, VO₂max readings and your Fit Age, walking steadiness, speed and asymmetry, time in daylight, environmental sound level, steps, active and basal energy, and exercise minutes.
  - **Check-ins:** mood, energy, stress, anxiety, meditation minutes, the time you checked in, any note, the Mind score, and whether you journaled that day (never what you wrote).
  - **Food you logged in Axon:** each entry (meal, name, quantity, calories, protein, carbohydrates, fat, fibre, time), the day's totals, your maintain and target numbers, and net energy.
  - **Health warnings** Axon raised, in the app's words.
  - **Profile facts the scores depend on:** age, sex, height, weight, unit choice, nutrition goal, time zone, the app's current day (when your day starts and ends), whether an Apple Watch is providing readings, how far back the history goes, and the app version.
  The last 120 days are uploaded once, then each new or changed day.
- **What never leaves:** raw Apple Health samples, dietary data read from Apple Health (section 1), the words of your journal entries, your calendar, and your name, email or Apple identifier.
- **Under what identity:** a **random connection ID** generated on your phone and kept in its Keychain (on this iPhone only, never in a backup). It is not your Apple identifier, is not derived from it and is never stored alongside it. It is also separate from the contribution ID in section 3: the two random IDs are kept apart and never joined, by us or by the service. The copy is stored in our backend (Supabase, on AWS). We store only a one-way hash of the **connect key** shown to you once on your phone, never the key itself.
- **Who can read it:** an assistant can read the copy **only with the connect key** — only an assistant you give the key to, through Axon's connection service. Axon's operator can access its own database in order to run the service (keep it working, fix faults, delete what must be deleted), and never reads the copy for any other purpose. You decide which assistant and where it runs; what that assistant's provider does with what it reads is governed by that provider's own privacy policy. If you set up an assistant with a command-line tool (for example Claude Code), that tool stores the key in its own settings on that computer.
- **Logging for you (on by default, can be switched off):** your assistant can ask Axon to log a mood check-in, a meal or a nap. The request waits on our backend until your phone next updates, where the app applies it with the same rules as an entry you make by hand, or declines it with a reason the assistant can read. Requests are deleted with the copy.
- **Turning it off** ends the key and deletes the whole copy, every request your assistant made (applied or not) and the key records, in one step. If your phone is offline at that moment, it stops sharing at once and the deletion runs the next time it reaches our backend. **Erase / Delete Account** (section 5) deletes all of it too; if that cannot reach our backend, this iPhone keeps the connection ID (in its Keychain) and completes the deletion the next time it can.
- **If your phone stops updating it:** a connection that has not been updated from your phone for **45 days** ends by itself — the key stops working and the copy, the requests and the key records are deleted. A weekly check removes any that no assistant asked for in the meantime.
- We keep only a daily count of how many reads and writes each connection made (under a one-way hash of the connection ID, with no health values), to protect the service from abuse and to know how many people use the feature.

## 4. Per-report: feedback diagnostics (off by default)

When you send in-app feedback, you can flip **"Attach diagnostic data"** for that report. If you do, the report includes your last 14 days of scores and recent app logs so we can debug your issue. This attachment is tied to your account (so we can reply to *your* problem) and is used only for handling that report. The toggle is off by default and applies to a single report at a time.

## 5. Account deletion — real and immediate

**Profile → Delete Account** permanently deletes, in one action:

- all local data on your device (scores, check-ins, journal, settings, sign-in state), and
- all server rows tied to your account — profile (including email), usage events, feedback, logs — and any contributed health data under your device's contribution ID.
- *(Draft, 2.1)* everything held for **Connect Axon to my AI assistant** (section 3a) — the copy, the key records and any pending requests.

Deletion is executed by a dedicated server-side function; it is not reversible. You can also email us (below) for deletion.

## 6. Third parties

| Service | What it receives | What it never receives |
|---|---|---|
| **Supabase** (supabase.com, on AWS) | Account profile, usage events (keyed by your Apple identifier when you are signed in, by the random per-install identifier when you are not), feedback, opt-in contributions, opt-in diagnostics; *(draft, 2.1)* while you keep it on, the copy for your AI assistant (section 3a), under its own random connection ID | Health values outside the opt-ins; journal entries; your calendar; device context or a session identifier on the anonymous records |
| **PostHog** (posthog.com, US Cloud) | Usage events + device context — keyed by an anonymous per-device identifier until you sign in, by your Apple sign-in identifier after | Any health value; your email or name; journal entries |

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
