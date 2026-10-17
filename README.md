# AttendTa v2 · Student Organization Event & Attendance System

AttendTa v2 is the static prototype of a university student-organization event platform: event publishing, student RSVPs, door passes, live attendance check-in, and certificate issuance — rebuilt on an *Institutional Precision* design system and structured as a mechanical port target for **ASP.NET Core Razor Pages** (see `RAZOR-PORT.md`).

**Status:** Prototype complete — Phases 0–5 of `IMPLEMENTATION_PLAN.md` verified; documentation finalized in Phase 6. **Event Moods** (live-event student backdrop + Live-Now hero + Tier 1 accent takeover) shipped as an add-on (UI-0.5 → UI-4, 2026-10-16; final cut 2026-10-17).

---

## Quick start

Zero dependencies, zero build. Serve the folder with Python 3:

```bash
python server.py
```

Then open **http://localhost:3000**.

> Tailwind is loaded from the Play CDN (dev-only), so the first load needs network access.

---

## Pages (22)

| # | Area | Page | Path |
|---|---|---|---|
| 1 | Public | Gateway — showcase, live band, directory | `index.html` |
| 2 | Auth | Sign in | `account/login.html` |
| 3 | Auth | Membership request | `account/register.html` |
| 4 | Officer | Account approval queue | `account/approvals.html` |
| 5 | Student | Browse events + Live-Now hero (mood backdrop) | `student/events.html` |
| 6 | Student | Event dossier (quiet backdrop) + cancel RSVP | `student/details.html?eventId=ev-1` |
| 7 | Student | Door passes (gate codes, print / save) | `student/passes.html` |
| 8 | Student | Attendance history | `student/history.html` |
| 9 | Officer | Door scanner kiosk | `kiosk/index.html` |
| 10 | Officer | Event operations | `events/index.html` |
| 11 | Officer | Create event (save draft / publish, mood picker) | `events/create.html` |
| 12 | Officer | Roster, waitlist, promote, roster CSV | `events/details.html` |
| 13 | Officer | Member records + status toggle | `masterdata/members.html` |
| 14 | Officer | Event types (add / archive) | `masterdata/eventtypes.html` |
| 15 | Officer | Venues | `masterdata/venues.html` |
| 16 | Officer | Add venue | `masterdata/venue-create.html` |
| 17 | Officer | Certificate issuance (single + batch) | `certificates/index.html` |
| 18 | Public | Certificate view / print (A4) | `certificates/view.html` |
| 19 | Officer | Participation report + CSV | `reports/participation.html` |
| 20 | Admin | Users + status toggle | `admin/users.html` |
| 21 | Admin | Appoint user — 8 permission scopes, 3 presets | `admin/user-create.html` |
| 22 | Admin | Audit log | `admin/auditlogs.html` |

`student/details.html` accepts `?eventId=` (or `?id=`).

---

## Key features

- **Door scanner kiosk** — camera QR scanning via `jsQR` when permission is granted; otherwise pass-code or student-number manual entry. Duplicate-scan window, `aria-live` narration, and a full-screen gate flash.
- **Event Moods** — two restrained live-event backdrops (Drift / Bloom, plus Plain) on the student views only; while an event is live the student shell repaints in the event accent (ground wash + header rule — "Tier 1" takeover). The Events page upgrades the live band into a single elevated Live-Now hero card. Officers pick the mood (type-suggested) when creating or editing an event; the backdrop color still follows the event type. Reduced motion freezes each mood to a static composition; print never shows one. Register: `assets/DESIGN-TOKENS.md` §Event Moods.
- **Door passes** — every pass carries a gate code (`AT-XXXX-XXXX`); print and save-image (canvas PNG) exports; `active` / `used` / `revoked` states.
- **Event lifecycle** — draft → publish; promotion from waitlist; roster CSV export.
- **Certificates** — eligibility list, single and batch issuance, public print-ready view.
- **Reports** — turnout metrics and filters, CSV export.
- **Admin** — 3 role presets (Administrator / Officer / Staff) over 8 permission scopes in 4 grouped cards; audit logging.
- **Design system** — `tokens.css` + plain-CSS components, one canonical Tailwind config, the Ink Seam signature element on 4 pages, reduced-motion honored globally.

---

## Architecture

| File | Role |
|---|---|
| `assets/tokens.css` | Design tokens — palette, type, spacing (register: `assets/DESIGN-TOKENS.md`) |
| `assets/components.css` | Component layer, plain CSS (no `@apply`) |
| `assets/app.js` | `Ta` runtime — store, toast, dialog, nav, kiosk, export, mood |
| `assets/tailwind.config.js` | Canonical Tailwind config (single source; pages do not inline configs) |
| `assets/icons.svg` | Icon sprite (`<use href>`) |
| `assets/ink-seam.css` / `.js` | Ink Seam — `index`, `account/login`, `account/register`, `certificates/view` only |
| `js/qr-engine.js` | Legacy prototype-era helper; **not referenced** — do not port |
| `server.py` | Python 3 stdlib dev server (port 3000) |

**Data layer:** `Ta.store` simulates a database in `localStorage` under `attendta:v2:*` (`members`, `users`, `approvals`, `types`, `venues`, `events`, `registrations`, `passes`, `certificates`, `auditlog`, `scans`, plus `session`, `prefs`, `sidebar`). Seed data loads on first visit. The swap list for EF Core entities is `RAZOR-PORT.md` §5.

**Forms contract:** every flow is a real `<form method="post">` with a `data-action` naming the future Razor handler (`OnPost*Async`); `app.js` enhances only. The frozen 22-handler map is `RAZOR-PORT.md` §4.

---

## Verification

No lint, typecheck, or test suite exists in the prototype; the stated bar (`IMPLEMENTATION_PLAN.md` §9) is the foundation checker plus manual passes:

```bash
python scratch/check_v2_ui.py --strict
```

The gate covers foundation markup rules (single `h1`, sprite + alt conventions, no inline handlers / `alert` / `confirm`, token-only color, focus + reduced-motion hooks, and more) and currently reports **TOTAL 0**.

Evidence lives in `scratch/`: desktop and 390px screenshots, print PDFs (pass / certificate / report), the mobile probe rig, and the Event Moods set (all moods × accent families, live/quiet/none details states, freeze probe, create → publish → student-view trace).

---

## Deferred (documented, not shipped — plan §12)

- Dark-mode token values.
- Tailwind compile step (done at the Razor port, not in the prototype).
- Server-side persistence replacing `Ta.store`.
- Full-site "live event takeover" — Event Moods ship **student-side only** (the Tier 1 wash + header rule repaint the student shell while live); public `index.html`, passes, and all officer/admin surfaces stay neutral (`plan.md` §10 has the open calls).

---

## Tech stack

- Semantic HTML5 + Tailwind Play CDN (dev-only) + plain-CSS components
- Vanilla ES6 (`assets/app.js`); `jsQR` (CDN) for kiosk camera decoding
- Python 3 standard library server
- **Target:** ASP.NET Core Razor Pages (.NET 8/9) — `RAZOR-PORT.md`

---

© 2026 USTP Student Organization Council · AttendTa Event Management System
