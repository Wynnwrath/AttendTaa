# AttendTa v2 — UI/UX Implementation Plan

**Revision 2 · 2026-10-15** (supersedes Rev 1)
**Scope:** All 22 HTML pages in `F:\AttendTa\v2`
**Delivery target:** **ASP.NET Core Razor Pages + Tailwind CSS.** The static v2 prototype exists only to be ported — nothing in this plan may depend on anything Razor can't reproduce (see §3).
**Prototype stack:** Static HTML + Tailwind (CDN, dev-only) + `assets/*.css` + vanilla ES6; zero-build; run via `python server.py` (localhost:3000). No lint/typecheck/tests exist in v2.
**Goals source of truth:** `F:\AttendTa\UC-Project-FL.pdf` (12 functions) + `WBS_AttendTa_Final_Documentation.md` (20 modules).
**Strategy:** v2 markup is **temporary** — we rebuild it against a new system, preserving only the 22 routes and the amber/ink direction.

---

## 0. Decisions log (locked unless vetoed)

| # | Decision |
|---|---|
| 1 | **Officer/Admin shells use a left sidebar** on ≥1024px (drawer below); Student/Public keep top nav; Kiosk is fullscreen. |
| 2 | **Event accent system — light version:** 8 AA-calibrated type accents (WBS "custom color badge tag") + a "LIVE NOW" band on the student feed. No full-site takeover. |
| 3 | Index "quick lookup" gizmo is **cut**; replaced by a real pass-status check wired to the demo store. |
| 4 | **Checkpoint git commit of `v2/` before the rebuild** — Phase 0, requires explicit user approval (`v2/` is currently 100% untracked). |
| 5 | Build is orchestrator-direct; the subagent pipeline is optional (the 6 md agent models are still broken — fix only if the pipeline is wanted). |

## 1. Findings (evidence, post-revert audit)

1. **Two design generations coexist.** Canonical amber/ink (Outfit) on only `index.html`, `kiosk/index.html`, `student/events.html`, `student/passes.html`; legacy blue-600/Plus Jakarta on the other 18.
2. **Shells duplicated inline** per page; active nav hardcoded; user chip content drifts.
3. **A11y gaps:** 0/22 have `prefers-reduced-motion`, `focus-visible`, or `aria-modal`; `alert()/confirm()` in `events/details.html` + `student/details.html`; inline `onclick/onchange` in 8 pages; `th` without `scope`.
4. **Motion drift:** `transition-all` in 19/22 pages; hover effects on every element.
5. **State drift:** `localStorage` demo persistence on 3 pages only; no toasts, no empty/loading/error states.
6. **Anti-slop status: halfway.** Remaining AI fingerprints: all-caps eyebrows, `•`-joined meta strings, uniform cards, `→` link text, glyph icons, placeholder data.
7. **Inline `tailwind.config` duplicated in all 22 pages.**
8. **Disk state (Rev 2 audit):** `tokens.css` exists (103-line reduced version — extend in Phase 2); `components.css`, `app.js`, `tailwind.config.js`, `icons.svg` are absent. `v2/` is untracked in git with no checkpoint.

## 2. Design direction (locked)

**Tone — "Institutional Precision":** registrar ledger × operations console. Quiet, dense, authoritative.
- One brand accent: amber. Status colors functional only. Event accents scoped to event surfaces only.
- Typography: Outfit (sans), JetBrains Mono (values only), Cinzel (certificates/print only).
- Density: public/auth/student = comfortable; officer/admin/kiosk = compact (hairlines, no card boxes for data, mono numbers).
- Domain vocabulary: registrar, dossier, muster, gate, credential, ledger, seal, roster.

**Palette rules (contrast-measured; published in `assets/DESIGN-TOKENS.md`):**

| Token | Value | Use / Never for |
|---|---|---|
| `--ink-primary` | `#090D16` | All text; never pure `#000` |
| `--ink-secondary` | `#334155` | Body |
| `--ink-muted` | `#64748B` | Min for small text |
| `--ink-faint` | `#94A3B8` | **Decorative only — never text** (slate-400-as-text is banned) |
| `--accent-amber` | `#D97706` | Large text/icons/UI only — never small text |
| `--accent-amber-deep` | `#B45309` | Small amber text/links |
| `--status-emerald` | `#059669` | Badges/large; small text `#047857` |
| `--status-rose` | `#DC2626` | Errors/destructive only |

**Type scale (with floors):** body 15px (comfortable shells) / 14px (compact shells); labels + meta ≥12px; nothing below 11px (kbd/mono chips only). Line-height 1.5 body, 1.25 headings. Density comes from spacing, never from shrinking type.

**Spacing scale:** 4 / 8 / 12 / 16 / 24 / 32 / 48. Two density modes applied per shell.

**Event accent palette (light system, WBS-mandated):** 8 accents — moss, indigo, teal, violet, crimson, orange, slate-blue, amber-default — each with `base` / `deep` (AA small text) / `subtle` (badge bg) / `glow`. Applied only to: type badges, event card hairline, dossier header rule, capacity gauge, LIVE band, pass strip, kiosk session chip, history ticks, report bars. Never nav, admin tables, buttons, status colors, or certificates.

**Radii & elevation:** radii 6 / 10 / 16 / pill only; **max one elevated surface per view**; hairline borders everywhere else.

**Token register:** hairlines, shadows (tactile/subtle/modal/flash), motion 120/180/240ms `cubic-bezier(0.2,0,0,1)`, focus ring 2px + 2px offset, z-scale 30/40/50/60, reduced-motion block, `.btn-tactile` press **scale(0.96)**, `.tabular-nums`, `.key-pill`.

**Anti-slop rules (verified in Phase 5):**
1. No decorative ALL-CAPS eyebrows (metadata labels only: IDs, dates, status).
2. No `•`-joined meta strings → hairline clusters / field groups.
3. Radius by hierarchy; max one elevated card per page.
4. Mono for actual values only.
5. No `→` link text (sprite chevron); no glyph icons.
6. Organic, messy realistic data.
7. Exact-property transitions; entrance motion only for the two signature moments.
8. **No dead controls:** every interactive element works; no prefilled credentials; no `href="#"`.
9. **One name per feature** across all shells (no "Vault" / "History" / "Records" triple naming).
10. **Media budget:** covers ≤250KB, all `img` have `width`/`height`, below-fold images lazy.

**Craft invariants:** no font pop-in (`display=swap` + `document.fonts.ready` gating); above-fold logo/headline paints first (`fetchpriority="high"`).

## 3. Razor Pages + Tailwind architecture (port contract)

Everything in this plan is designed for mechanical porting to Razor Pages:

- **Routes frozen:** all 22 file paths stay identical. Port map: `v2/account/login.html` → `Pages/Account/Login.cshtml`, etc. `server.py` clean URLs mirror `@page` routes.
- **Shells → layouts/partials:** each shell becomes `_Layout` variants + partials: `_Header`, `_SideNav` (officer/admin sidebar), `_Breadcrumb`, `_Footer`, `_FlashHost`. Active nav via tag helper using route data (prototype uses `data-nav` + `aria-current` logic in `TaNav`).
- **Progressive enhancement:** every flow is a real form `POST` first; static `method`/`action` + `data-action` names mirror future `asp-page-handler` names (recorded in `RAZOR-PORT.md`). JS (`app.js`) only *enhances*: dialogs, toasts, drawer, table filter, kiosk behavior. No SPA patterns.
- **Tailwind:** one canonical `tailwind.config.js`; prototype loads CDN (dev-only); at port, Tailwind CLI compiles to `wwwroot/css` — tokens stay as CSS variables so one palette serves both.
- **State:** `TaStore` (namespaced `attendta:v2:*` localStorage) → EF Core entities; swap list in `RAZOR-PORT.md`. Flash messages → `TempData` + `_FlashHost` partial (toasts in prototype).
- **CSP note:** Tailwind CDN needs `unsafe-eval`; production compiles Tailwind and can enforce strict CSP.
- The prototype's markup discipline (semantic forms, `data-*` hooks, duplicated shells kept in lockstep) exists so the port is mechanical.

## 4. Foundation (Phase 2)

| File | Status | Content |
|---|---|---|
| `v2/assets/tokens.css` | rebuild | Full token register: fonts, ink/canvas/amber/event-accents/status, radii, hairlines, shadows (incl. `--shadow-flash`), motion trio, `:focus-visible`, reduced-motion, density hooks, `.btn-tactile`@0.96, `.tabular-nums`, `.key-pill` |
| `v2/assets/components.css` | new | `.btn` (4 variants × 3 sizes), `.field/.input/.select/.textarea/.checkbox/.switch` + label/help/error, `.card-hairline`, `.table-ledger` (sticky thead, tabular-nums, card fallback <640px), `.badge/.status-pill`, `.tabs`, `.breadcrumb`, `.drawer`, `.sidenav`, `.menu`, `.dialog`, `.toast`, `.empty-state`, `.skeleton`, `.timeline`, `.gauge`, `.steps`, `.viewfinder` (kiosk), `.pass-card`, print styles (pass / certificate / report) |
| `v2/assets/app.js` | new | `TaToast`; `TaDialog.confirm()` (promise, focus trap, Esc, `aria-modal`); `TaNav` (pathname → `aria-current`); `TaSidebar` (collapse state, persisted); `TaDrawer` (mobile, scroll lock); `TaTable` (search/filter/sort/empty); `TaForm` (inline validation, disable-on-submit); `TaStore` (namespaced localStorage + seed + cross-tab sync); `TaKiosk` (3 input modes, scan queue, 2s duplicate suppression, `aria-live`); `TaExport` (CSV + pass image); `TaMotion` (reduced-motion guard). All `data-*` event delegation — zero inline handlers |
| `v2/assets/icons.svg` | new | ~40-icon sprite, stroke 1.5/2, `currentColor` |
| `v2/assets/tailwind.config.js` | new | One canonical config (fonts, ink/canvas/amber/event/status → CSS vars, radii, shadows) replacing 22 inline copies |
| `v2/assets/DESIGN-TOKENS.md` | new | Token register: value, contrast ratio, WCAG level, "Do Not Use For" (incl. 8 event accents) |
| `v2/RAZOR-PORT.md` | new | Page map (22 → `.cshtml`), handler map (`data-action` → `asp-page-handler`), partial map, localStorage → server swap list, Tailwind compile step, CSP note |

## 5. Shells & page anatomy

| Shell | Pages | Chrome |
|---|---|---|
| Public | `index` | Light top nav: logo + AY badge + Door Scanner + Sign In |
| Auth | `account/login`, `account/register` | Centered minimal, logo only |
| Student | `student/*` (4) | Top nav + student chip + passes badge |
| Officer/Admin | `events/*`, `masterdata/*`, `certificates/*`, `reports/*`, `account/approvals`, `admin/*` (15) | **Left sidebar** (grouped: Operations / People / Records; approvals badge) + top bar (role chip, Sign Out) + breadcrumbs |
| Kiosk | `kiosk` | Fullscreen, no nav, ≥56px targets |

**Standard page anatomy:** page header (title + context + primary action) → toolbar (search / filter / export) → content (table / grid) → states. **Forms:** two-column (form + context panel) with sticky action bar. **Mobile <1024px:** sidebar → drawer; tables → card fallback; breadcrumbs on all detail pages; skip-link on all pages.

## 6. Waves — rebuild all 22 pages

**Wave A — Public/Auth (4)**
- `index.html` — hero + LIVE/NEXT event band + role gateways; cut quick-lookup → real pass-status check (store-backed); font gating; og tags.
- `account/login.html` — rebuild: demo persona chips (Student/Officer/Admin, WBS-mandated), inline validation, `autocomplete`; no prefilled credentials.
- `account/register.html` — field errors; approval-flow clarity; institutional email + student number validation.
- `account/approvals.html` — reject confirm dialog; approve toast; empty state; auto-enroll hook.

**Wave B — Student (4)**
- `student/events.html` — working filter chips (aria-pressed); type accents on cards; LIVE banner; empty state.
- `student/details.html` — dialog replaces `alert/confirm`; RSVP state machine (idle → submitting → confirmed / waitlisted); breadcrumbs.
- `student/passes.html` — pass card w/ event accent strip; print stylesheet; Save/Download image; de-inline.
- `student/history.html` — rebuild; ledger timeline with accent ticks; certificates access; empty state.

**Wave C — Officer (11)** *(all pages rebuilt into the sidebar shell)*
- `kiosk/index.html` — session chip (event accent); 3 input modes (camera QR / manual search / student-no keypad); scan log; gate-flash signature; camera-denied / invalid / duplicate states; `aria-live`.
- `events/index.html` — table w/ working filters, Active/Archived tabs; row menu; CSV.
- `events/create.html` — sectioned form + sticky action bar; inline validation.
- `events/details.html` — tabbed workspace: Roster | Waitlist | Attendance | Certificates; promote waitlist; CSV roster export.
- `masterdata/members.html` — de-inline; `TaStore`; bulk-select; status toggle; empty state.
- `masterdata/venues.html`, `venue-create.html`, `eventtypes.html` — rebuilt; **event type color tags = accent picker** (8 presets).
- `certificates/index.html` — eligibility override + batch issue → confirm + progress + toast.
- `certificates/view.html` — print-first; Cinzel seal; credential ID.
- `reports/participation.html` — KPI row + no-show table + course/year charts; CSV + print.

**Wave D — Admin (3)**
- `admin/users.html` — rebuild; `TaStore`; revoke confirm; filters.
- `admin/user-create.html` — grouped permission scope cards; validation.
- `admin/auditlogs.html` — rebuild; filter by actor/action/date; empty state.

## 7. UX states, flows & functional alignment

- `TaStore` unifies demo persistence across all 22 pages (keys: `attendta:v2:members|users|approvals|events|types|venues|registrations|passes|certificates|auditlog|session`).
- **UC-Project-FL & WBS Mandatory Functional Workflows:**
  1. **Auto-Enrollment Pipeline:** approving a request in `account/approvals.html` provisions a member in `masterdata/members.html`, carrying over the submitted student number + institutional email (no regeneration — WBS duplicate-prevention); type `Member`, status `active`.
  2. **Capacity & Waitlist State Machine:** registration validates seat limits; full → `waitlisted`; officers promote to `confirmed` with instant badge updates.
  3. **Multi-Mode Kiosk Check-In:** camera QR + manual search + student-number keypad; every check-in timestamped.
  4. **Attendance-to-Certificate Auto-Eligibility:** check-ins unlock eligibility in `certificates/index.html`; officer manual override retained (UC #10); batch issue + PDF view.
  5. **Demographic & No-Show Reporting:** turnout %, No-Show List (Registered vs Attended), course/year distribution.
  6. **WBS-Mandated Exports (client-side Blob):** roster CSV (`events/details`), report CSV (`reports/participation`), pass image save (`student/passes`).

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

- Toasts on every mutating action; confirm dialogs on destructive ones (reject, revoke, cancel RSVP).
- Inline validation on: login, register, create event, venue create, user create.
- Empty/loading/error states for every table/list.
- Print: pass, certificate, report.
- Idempotency: disable submit while in-flight.

## 8. Signature elements (exactly two)

1. **"The Ink Seam"** — 160px SVG strip at main→footer on `index`, `account/login`, `account/register`, `certificates/view` only. Ink `#0B1120` → parchment, 1px amber seal-line. Idle layered drift (transform-only); pointer bulge (rAF-lerped). Fallbacks: static under reduced-motion / no-JS; `aria-hidden`; bounded hit area. Ports as a footer-partial asset.
2. **Kiosk gate flash** — full-width success moment (uses `--shadow-flash`), narrated by `aria-live="assertive"`.

## 9. Verification (Phase 5)

`scratch/check_v2_ui.py` (Python stdlib, exit-code gate):
1. All 22 pages import `tokens.css` + `components.css` + `app.js`; no inline `tailwind.config`.
2. No `onclick=|onchange=|onsubmit=|alert(|confirm(`.
3. No `transition-all`; no `#000` classes.
4. No duplicate IDs; every input has `<label for>`/`aria-label`; every `img` has `alt`; every `th` has `scope`; exactly one `<h1>` per page.
5. Internal links resolve (extend `scratch/check_v2_links.py`).
6. Contrast ratios for every text-on-surface token pair; fail under AA.
7. `prefers-reduced-motion` + `:focus-visible` present; press scale = 0.96.
8. Ink Seam on exactly the 4 approved pages, `aria-hidden`, with fallbacks.
9. **Design guardrails:** full-height views use `min-h-[100dvh]` (never `h-screen`); critical headline surfaces gated via `document.fonts.ready`; three interactive traces audited: (a) Student RSVP → QR Pass, (b) Kiosk Scan → Certificate Eligibility, (c) Approval → auto-provisioned Member.
10. WBS export actions present and wired: roster CSV, report CSV, pass save/download.
11. **Type floor:** no text utility below 12px except kbd/mono chips (≥11px).
12. **No slate-400/ink-faint as text color.**
13. **Media budget:** cover images ≤250KB, all `img` have `width`/`height`; below-fold `loading="lazy"`.
14. **No dead controls:** no prefilled credentials; no `href="#"`; filter controls verify behavior.
15. **Radius whitelist:** only the token radii (6/10/16/pill) in new markup.
16. Event accents: all 8 pairs contrast-checked; accents never on nav/admin/buttons/status.

Then: **design-ux Nielsen scorecard** on kiosk, login, events/index, student/details, reports — fix loop to zero blockers. **Manual pass:** 390px (no horizontal scroll), keyboard-only kiosk + RSVP run, print previews of pass/certificate/report. No lint/typecheck/tests exist — this is the stated verification bar.

## 10. Execution pipeline

| Phase | Agent | Output | Gate |
|---|---|---|---|
| 0 | user | approve checkpoint commit of `v2/` (then orchestrator commits) | rollback possible |
| 1 | explore ×3 (optional) | shell/nav deltas, flow-audit deltas, per-page head blocks | merged into wave specs |
| 2 | build | Foundation files + `DESIGN-TOKENS.md` | check script v1 passes |
| 2.5 | build | Ink Seam + kiosk gate flash | check rule 8 + manual trace |
| 3 | build, one wave per run | Waves A → B → C → D | check script + spot review per wave |
| 4 | build | TaStore wiring, states, validation, print CSS, exports | check script + kiosk trace |
| 5 | verifier + evaluator | script result + scorecards | zero blockers |
| 6 | build | `README.md` + `RAZOR-PORT.md` final | — |

Note: if the subagent pipeline is unavailable (broken md agent models — Decision 5), the orchestrator builds directly; the same gates apply.

## 11. Timeline (4 weeks)

- **W1:** Foundation + check script + shells (sidebar + top nav).
- **W2:** Waves A + B + Ink Seam.
- **W3:** Waves C + D.
- **W4:** UX states, exports, verification, docs.

## 12. Deferred (documented, not shipped)

- Dark-mode token values.
- Tailwind compile step (done at Razor port, not in prototype).
- Server-side persistence replacing `TaStore`.
- Full-site "live event takeover" (only the light accent system + LIVE band ship).

## 13. Risks

- Sprite `<use>` MIME from `server.py` — verified OK (Python serves `image/svg+xml`), re-verify at port.
- `document.fonts.ready` gating — feature-check, fail open.
- 22-page sweep size — wave gates keep every stopping point coherent.
- Image compression tooling (Pillow availability unknown) — verify early; fallback: lazy-load + keep largest assets out of first viewport.

## 14. Acceptance checklist

- [ ] 22/22 pages rebuilt on the shared foundation; zero inline handlers; zero `alert/confirm`; zero dead controls
- [ ] Every action has toast/state feedback; every list has an empty state; nothing below the 12px floor
- [ ] Kiosk narrated by `aria-live`; camera-denied/invalid/duplicate handled; gate flash works
- [ ] Officer/Admin sidebar keyboard-accessible; drawer works <1024px
- [ ] Event accents: 8 presets, AA-checked, correctly scoped (never nav/admin/buttons/status)
- [ ] 390px clean on all pages; keyboard-only flows pass
- [ ] `prefers-reduced-motion` honored everywhere
- [ ] Print correct for pass, certificate, report; WBS exports wired (roster CSV, report CSV, pass save)
- [ ] Ink Seam on the 4 pages only, with all fallbacks
- [ ] Media budget met (≤250KB covers, dimensions set, lazy below fold)
- [ ] Anti-slop scorecard passes; design-ux scorecard shows zero blockers
- [ ] `RAZOR-PORT.md` complete: page/handler/partial maps + swap list
