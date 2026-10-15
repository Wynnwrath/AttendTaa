# AttendTa v2 — UI/UX Implementation Plan

**Date:** 2026-10-15
**Scope:** All 22 HTML pages in `F:\AttendTa\v2`
**Stack:** Static HTML + Tailwind (CDN) + `assets/tokens.css`; prototype for ASP.NET Core Razor Pages. Zero-build, zero-deps, run via `python server.py`. No lint/typecheck/tests exist in v2.
**Execution:** subagent pipeline (research → build → verify)

---

## 1. Findings (evidence)

1. **Two design generations coexist.**
   - Canonical amber/ink system (Outfit, `#090D16`, `#D97706`, hairlines): only `index.html`, `kiosk/index.html`, `student/events.html`, `student/passes.html` (the only pages importing `tokens.css`).
   - Legacy blue-600 / Plus Jakarta, no tokens: the other 18 pages (`account/*`, `admin/*`, `events/*`, `masterdata/*`, `reports/participation`, `student/details`, `student/history`, `certificates/*`).
2. **Shells duplicated inline** per page; active nav hardcoded (`events/index.html:38` vs `reports/participation.html:44`); user chip content drifts between pages.
3. **A11y gaps:** 0/22 pages have `prefers-reduced-motion`, `focus-visible`, or `aria-modal`; `alert()`/`confirm()` in `events/details.html` + `student/details.html`; inline `onclick/onchange` in 8 pages; `th` without `scope`.
4. **Motion drift:** `transition-all` in 19/22 pages.
5. **State drift:** `localStorage` demo persistence only on 3 pages; no toasts, no empty/loading/error states.
6. **Anti-slop status: halfway.** Remaining AI fingerprints: all-caps eyebrows above headings, `•`-joined meta strings, uniform card radius/shadow everywhere, `→` appended to link text, glyph icons (`✓`), placeholder-feel data, hover transitions on every element.
7. **Inline tailwind.config duplicated in all 22 pages** — drift risk.

## 2. Design direction (locked)

**Tone — "Institutional Precision":** registrar ledger × operations console. Quiet, dense, authoritative.
- One accent: amber. Status colors functional only.
- Canonical typography: Outfit (sans), JetBrains Mono (values only), Cinzel (certificates/print only).
- Density: public/auth/student = Daily-App; officer/admin/kiosk = Cockpit (hairlines, no card boxes for data, mono numbers).
- Domain vocabulary: registrar, dossier, muster, gate, credential, ledger, seal, roster.

**Palette rules (contrast-measured; publish in `assets/DESIGN-TOKENS.md`):**

| Token | Value | Use / Never for |
|---|---|---|
| `--ink-primary` | `#090D16` | All text; never pure `#000` |
| `--ink-secondary` | `#334155` | Body |
| `--ink-muted` | `#64748B` | Min for small text |
| `--ink-faint` | `#94A3B8` | Decorative only — never text |
| `--accent-amber` | `#D97706` | Large text/icons/UI only — never small text |
| `--accent-amber-deep` | `#B45309` | Small amber text/links |
| `--status-emerald` | `#059669` | Badges/large; small text `#047857` |
| `--status-rose` | `#DC2626` | Errors/destructive |

**Token additions:** radius 16/10/pill (concentric: outer = inner + padding); shadows tactile/subtle/modal/flash; motion 120/180/240ms `cubic-bezier(0.2,0,0,1)`; focus ring 2px + 2px offset; z-scale 30/40/50/60; reduced-motion block; `oklch(0 0 0 / .1)` image outlines; `.btn-tactile` press fixed to **scale(0.96)**.

**Anti-slop rules (verified in Phase 5):**
1. No decorative ALL-CAPS eyebrows (metadata labels only: IDs, dates, status).
2. No `•`-joined meta strings → hairline clusters / field groups.
3. Radius by hierarchy; max one elevated card per page.
4. Mono for actual values only.
5. No `→` link text (sprite chevron); no glyph icons.
6. Organic, messy realistic data.
7. Exact-property transitions; entrance motion only for the two signature moments.

**Craft invariants:** no font pop-in (`display=swap` + `document.fonts.ready` gating); above-fold (logo/headline) paints first (`fetchpriority="high"`).

## 3. Foundation (Phase 2)

| File | Status | Content |
|---|---|---|
| `v2/assets/tokens.css` | extend | ~136 lines on disk: fonts, ink/canvas/amber/status, radii, hairlines, shadows (incl. `--shadow-flash`), motion trio, `:focus-visible`, reduced-motion, `.btn-tactile`@0.96, `.tabular-nums`, `.key-pill`. Remaining: glass-subtle tier, image outline, z-scale tokens |
| `v2/assets/components.css` | extend | ~293 lines on disk: `.btn` 4 variants ×3 sizes, `.field-*`/`.input`/`.select`/`.textarea` + error states, `.card-hairline`, `.table-ledger`, `.badge` ×4, `.empty-state`, toast + dialog shells. Add: `.checkbox`, `.skeleton`, `.tabs`, `.breadcrumb`, `.drawer`, card-table fallback <640px |
| `v2/assets/app.js` | new | `TaToast`; `TaDialog.confirm()` (promise, focus trap, Esc, `aria-modal`); `TaNav` (pathname → `aria-current`); `TaDrawer` (mobile nav, scroll lock); `TaTable` (search/filter/empty toggle); `TaForm` (inline validation, disable-on-submit); `TaMotion` (reduced-motion guard); `TaStore` (namespaced `attendta:v2:*` localStorage + seed + cross-tab sync); `TaKiosk` (scan queue, 2s duplicate suppression, `aria-live`). All `data-*` event delegation — zero inline handlers |
| `v2/assets/icons.svg` | new | ~40-icon sprite, stroke 1.5/2, `currentColor` |
| `v2/assets/tailwind.config.js` | new | One canonical config (fonts, ink/scholastic/status → CSS vars, radii, shadows) replacing 22 inline copies |
| `v2/assets/DESIGN-TOKENS.md` | new | Token register: value, contrast ratio, WCAG level, "Do Not Use For" |
| `v2/RAZOR-PORT.md` | new | `_Layout`/`_Header`/`_RoleNav`/`_FlashHost` mapping; tag-helper active nav; `data-action` → `asp-page-handler` table; localStorage → server swap list; CSP note (Tailwind CDN needs `unsafe-eval`; compile at port) |

> **Disk state (audited 2026-10-15):** `tokens.css` (~136 lines) and `components.css` (~293 lines) already exist but are untracked in git (`?? v2/assets/`) — checkpoint commit before the sweep (ask user). Neither is referenced by any page yet; `app.js`, `icons.svg`, `tailwind.config.js` confirmed absent. Phase 2 = extend + complete, not from scratch.

## 4. Shell specification

| Shell | Pages | Header | Nav |
|---|---|---|---|
| Public | `index` | Logo + AY badge + "Door Scanner Desk" + Sign In | none |
| Auth | `account/login`, `account/register` | Logo-only | — |
| Student | `student/*` (4) | Logo + student chip | Events / My Passes / History |
| Officer | `events/*`, `masterdata/*`, `certificates/*`, `reports/*`, `account/approvals`, `admin/*` | Logo + role chip + Sign Out | Events / Master Records / Approvals (badge) / Reports |
| Kiosk | `kiosk` | Minimal + back + camera-health pill | — |

Mobile <768px: drawer nav; card-list table fallback on members, users, events, approvals. Breadcrumbs on all detail pages. Skip-link on all pages.

## 5. Waves (all 22 pages)

**Wave A — Public/Auth (4)**
- `index.html` — font-ready gating, og tags, chrome-reduction pass, token cleanup.
- `account/login.html` — full restyle blue→amber; inline validation; demo-credential chips; cut helper-text walls; `autocomplete` attrs.
- `account/register.html` — restyle; field errors; clarity of approval flow.
- `account/approvals.html` — restyle; confirm dialog on reject; toast on approve; empty state.

**Wave B — Student (4)**
- `student/events.html` — token cleanup, filter consolidation, empty state.
- `student/details.html` — replace `alert/confirm` with `TaDialog`; RSVP button state machine (idle → submitting → confirmed); breadcrumbs.
- `student/passes.html` — de-inline handlers; print stylesheet; QR card → image outline; Save/Download pass image (WBS).
- `student/history.html` — full restyle (pure-blue legacy); ledger timeline; empty state.

**Wave C — Officer (11)**
- `kiosk/index.html` — de-inline handlers; `aria-live` result region; camera-denied / invalid-QR / duplicate-scan states; gate-flash signature; ≥56px targets.
- `events/index.html` — nav active fix; row actions → menu; filter chips.
- `events/create.html` — sectioned form; inline validation; sticky action bar.
- `events/details.html` — de-inline; `alert/confirm` → dialog; roster/waitlist actions; CSV export attendee roster (WBS).
- `masterdata/members.html` — de-inline; unify to `TaStore`; bulk-select; empty state.
- `masterdata/venues.html`, `masterdata/venue-create.html`, `masterdata/eventtypes.html` — shell + states + validation.
- `certificates/index.html` — batch issue → confirm + progress + toast.
- `certificates/view.html` — print stylesheet; Cinzel seal; de-inline.
- `reports/participation.html` — de-inline `window.print`; per-scope empty state; keep print layout; CSV export (WBS).

**Wave D — Admin (3)**
- `admin/users.html` — de-inline + `TaStore`; revoke confirm; filters.
- `admin/user-create.html` — grouped permission scope cards; validation.
- `admin/auditlogs.html` — full restyle; filter by actor/action/date; empty state.

## 6. Signature elements (exactly two)

**1. "The Ink Seam"** — 160px SVG strip at main→footer on **`index`, `account/login`, `account/register`, `certificates/view` only**:
- Layers: ink `#0B1120` → parchment `#F8FAFC`, 1px amber seal-line `rgba(217,119,6,.35)`.
- Idle: slow layered drift (transform-only, different speeds per layer).
- Pointer: soft bulge follows cursor X (one quadratic control point, rAF-lerped).
- Fallbacks: static under `prefers-reduced-motion` / no-JS; idle-only on touch; `aria-hidden="true"`; bounded hit area.
- Razor: static asset + markup in the shared footer partial; documented in `RAZOR-PORT.md`.

**2. Kiosk gate flash** — full-width verification moment on successful check-in (uses `--shadow-flash`), narrated by `aria-live="assertive"`.

## 7. UX states & flows (Phase 4 & Functional Alignment)

- `TaStore` unifies demo persistence across all 22 pages (keys: `attendta:v2:members|users|approvals|events|registrations|passes|certificates|auditlog|session`).
- **UC-Project-FL & WBS Mandatory Functional Workflows:**
  1. **Auto-Enrollment Pipeline:** Approving a student account request in `account/approvals.html` instantly provisions a record in `masterdata/members.html`, carrying over the submitted student number + institutional email (no regeneration — WBS duplicate-prevention); membership type `Member`, status `active`.
  2. **Capacity & Waitlist State Machine:** Online registration (`student/details.html` / `events/details.html`) strictly validates seat limits; when full, sets status to `waitlisted`. Officers can promote waitlisted participants to `confirmed` with instant badge updates.
  3. **Multi-Mode Kiosk Attendance Check-In:** `kiosk/index.html` provides 3 input channels:
     - Live camera QR scanning with targeting reticles and audio chime.
     - Manual participant search by name.
     - Direct Student Number keypad input (critical fallback for camera-denied or damaged screens).
  4. **Attendance-to-Certificate Auto-Eligibility:** Check-ins recorded at the kiosk automatically update event attendance logs and unlock certificate eligibility in `certificates/index.html`; officer manual override (mark eligible / event-completion approval) retained per UC #10; then 1-click batch issuance + PDF view.
  5. **Demographic & No-Show Participation Reporting:** `reports/participation.html` computes turnout rate (%), generates an automated **No-Show List** (Registered vs. Attended), and breaks down course/year demographic distribution.
  6. **WBS-Mandated Exports (client-side Blob):** attendee roster CSV (`events/details.html`), participation report CSV (`reports/participation.html`), Save/Download QR pass image (`student/passes.html`).

**UC-Project-FL traceability (12 functions → wave → verification):**

| UC # | Function | Page(s) | Wave | Verified by |
|---|---|---|---|---|
| 1 | User Login (student no. OR email) | `account/login` | A | persona redirect trace |
| 2 | Role-Based Access | login redirect + role shells | A | persona redirect trace |
| 3 | Account Registration Approval | `account/register`, `account/approvals` | A | trace c (→ member) |
| 4 | Organization Member Management | `masterdata/members` | C | spot review |
| 5 | Event Type Management | `masterdata/eventtypes` | C | spot review |
| 6 | Venue Management | `masterdata/venues`, `venue-create` | C | spot review |
| 7 | Event Creation & Posting | `events/index`, `events/create` | C | spot review |
| 8 | Online Event Registration | `student/events`, `student/details`, `events/details` | B/C | trace a (RSVP → pass) |
| 9 | Attendance Check-In | `kiosk/index` | C | trace b (scan → eligibility) |
| 10 | Certificate Eligibility Tracking | `certificates/index`, `certificates/view` | C | trace b |
| 11 | Event Participation Report | `reports/participation` | C | check script + print |
| 12 | Officer & Permission Management | `admin/users`, `user-create`, `auditlogs` | D | spot review |

- Toasts on every mutating action; confirm dialogs on destructive actions (reject, revoke, cancel RSVP).
- Inline validation on: login, register, create event, venue create, user create.
- Empty/loading/error states for every table/list.
- Print: pass, certificate, report.
- Idempotency: disable submit while in-flight (`design-ux`).

## 8. Verification (Phase 5)

`scratch/check_v2_ui.py` (Python stdlib, exit-code gate):
1. All 22 pages import `tokens.css` + `components.css` + `app.js`; no inline `tailwind.config` remains.
2. No `onclick=|onchange=|onsubmit=|alert(|confirm(`.
3. No `transition-all`; no `#000` classes.
4. No duplicate IDs per file; every input has `<label for>`/`aria-label`; every `img` has `alt`; every `th` has `scope`; exactly one `<h1>` per page.
5. Internal links resolve (extend `scratch/check_v2_links.py`).
6. Contrast ratios computed for every text-on-surface token pair; fail under AA.
7. `prefers-reduced-motion` + `:focus-visible` present; press scale = 0.96.
8. Ink Seam present on exactly the 4 approved pages, `aria-hidden`, with fallbacks.
9. **Design Skills Guardrails:**
   - Full-height views use `min-h-[100dvh]` (never `h-screen`) to prevent mobile Safari/Chrome address-bar jumps (`design-taste-frontend`).
   - Anti-font pop-in: critical headline surfaces gated via `document.fonts.ready` (`design-thinking`).
   - Three interactive traces audited: (a) Student RSVP → QR Pass, (b) Kiosk Scan → Certificate Eligibility, (c) Approval → auto-provisioned Member (`design-ux`).
10. WBS export actions present and wired: roster CSV, report CSV, pass save/download.

Then: **design-ux Nielsen scorecard** on kiosk, login, events/index, student/details, reports — fix loop to zero blockers. **Manual pass:** 390px width (no horizontal scroll), keyboard-only kiosk + RSVP run, print previews of pass/certificate/report. No lint/typecheck/tests exist — this is the stated verification bar.

## 9. Execution pipeline

| Phase | Agent (model) | Output | Gate |
|---|---|---|---|
| 0 | user | `opencode.json` done ✓; remaining: 6 agent `.md` models → `opencode/deepseek-v4.1-flash-free` (md files override config — `explore` works, `researcher`/`builder`/`verifier` fail `Model not found: opencode-go/deepseek-v4-flash`); restart | subagents respond |
| 1 | explore ×3 (low) | shell/nav deltas, flow-audit deltas, per-page head blocks | merged into wave specs |
| 2 | build (max) | Complete existing tokens/components; add `app.js`, `icons.svg`, `tailwind.config.js` + `DESIGN-TOKENS.md` | check script v1 passes |
| 2.5 | build (max) | Ink Seam + kiosk gate flash | check rule 8 + manual trace |
| 3 | build (max), one wave per run | Waves A → B → C → D | check script + spot review per wave |
| 4 | build (max) | TaStore wiring, states, validation, print CSS | check script + kiosk trace |
| 5 | verifier (high) + evaluator | script result + scorecards | zero blockers |
| 6 | build | `README.md` + `RAZOR-PORT.md` final | — |

## 10. Timeline (4 weeks)

- **W1:** Foundation + check script.
- **W2:** Waves A + B + Ink Seam.
- **W3:** Waves C + D.
- **W4:** UX states + verification + docs.

## 11. Deferred (documented, not shipped)

- Dark-mode token values.
- Tailwind compile step for production.
- Server-side persistence replacing `TaStore` at Razor port.

## 12. Risks

- Sprite `<use>` MIME from `server.py` — verify early.
- `document.fonts.ready` gating — feature-check, fail open.
- 22-page sweep size — wave gates keep every stopping point coherent.

## 13. Acceptance checklist

- [ ] 22/22 pages on shared foundation; zero inline handlers; zero `alert/confirm`
- [ ] Every action has toast/state feedback; every list has an empty state
- [ ] Kiosk narrated by `aria-live`; camera-denied/invalid/duplicate handled
- [ ] 390px clean on all pages; keyboard-only flows pass
- [ ] `prefers-reduced-motion` honored everywhere
- [ ] Print correct for pass, certificate, report; WBS exports wired (roster CSV, report CSV, pass save)
- [ ] Ink Seam on the 4 pages only, with all fallbacks
- [ ] Anti-slop scorecard passes; design-ux scorecard shows zero blockers