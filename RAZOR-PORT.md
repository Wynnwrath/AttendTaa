# AttendTa v2 — Razor Port Contract

**Status:** final port contract (Phase 6, 2026-10-16) · companion to `IMPLEMENTATION_PLAN.md` §3
**Source:** `F:\AttendTa\v2` (static HTML prototype, 22 pages)
**Target:** ASP.NET Core Razor Pages (.NET 8/9) + Tailwind CSS CLI

---

## 1. Overview

This document is the **contract for porting the static v2 prototype to ASP.NET Core Razor Pages**. The prototype is temporary markup built to be reproduced mechanically; it exists to fix the 22 routes, the shell anatomy, and the interaction hooks so the port has zero design decisions left to make.

**Frozen-route rule:** **No route may change during the port.** All 22 prototype file paths stay identical in meaning — each maps 1:1 to one `.cshtml` page with a matching `@page` route. `server.py` clean URLs mirror the Razor routes. If a route must change, it changes *before* the port, never during.

| Concern | Prototype | Target |
|---|---|---|
| Rendering | Static HTML, zero-build | Razor Pages server-rendered |
| CSS framework | Tailwind **Play CDN** (dev-only) | Tailwind **CLI** → `wwwroot/css/site.css` |
| Design tokens | `assets/tokens.css` (CSS custom properties) | same CSS custom properties (unchanged) |
| Components | `assets/components.css` (plain CSS) | copied as-is |
| Runtime JS | `assets/app.js` vanilla ES6, `window.Ta` | same file, served as external `wwwroot/js/app.js` |
| State | `Ta.store` localStorage (`attendta:v2:*`) | EF Core entities + auth cookie/claims |
| Flash messages | toasts via `TaToast` | `TempData` → `_FlashHost` partial |
| Forms | `method="post"` + `data-action` | same form + `asp-page-handler` |
| Nav state | `Ta.nav` sets `aria-current` on `a[data-nav]` | nav tag helper sets `aria-current="page"` |

---

## 2. Page map

All 22 rows. Razor page path is relative to the project `Pages/` folder; the `@page` route mirrors the prototype path.

| # | Prototype path | Razor page | Layout |
|---|---|---|---|
| 1 | `index.html` | `Pages/Index.cshtml` | `_LayoutPublic` |
| 2 | `account/login.html` | `Pages/Account/Login.cshtml` | `_LayoutAuth` |
| 3 | `account/register.html` | `Pages/Account/Register.cshtml` | `_LayoutAuth` |
| 4 | `account/approvals.html` | `Pages/Account/Approvals.cshtml` | `_LayoutOfficer` |
| 5 | `student/events.html` | `Pages/Student/Events.cshtml` | `_LayoutStudent` |
| 6 | `student/details.html` | `Pages/Student/Details.cshtml` | `_LayoutStudent` |
| 7 | `student/passes.html` | `Pages/Student/Passes.cshtml` | `_LayoutStudent` |
| 8 | `student/history.html` | `Pages/Student/History.cshtml` | `_LayoutStudent` |
| 9 | `kiosk/index.html` | `Pages/Kiosk/Index.cshtml` | `_LayoutKiosk` |
| 10 | `events/index.html` | `Pages/Events/Index.cshtml` | `_LayoutOfficer` |
| 11 | `events/create.html` | `Pages/Events/Create.cshtml` | `_LayoutOfficer` |
| 12 | `events/details.html` | `Pages/Events/Details.cshtml` | `_LayoutOfficer` |
| 13 | `masterdata/members.html` | `Pages/MasterData/Members.cshtml` | `_LayoutOfficer` |
| 14 | `masterdata/venues.html` | `Pages/MasterData/Venues.cshtml` | `_LayoutOfficer` |
| 15 | `masterdata/venue-create.html` | `Pages/MasterData/VenueCreate.cshtml` | `_LayoutOfficer` |
| 16 | `masterdata/eventtypes.html` | `Pages/MasterData/EventTypes.cshtml` | `_LayoutOfficer` |
| 17 | `certificates/index.html` | `Pages/Certificates/Index.cshtml` | `_LayoutOfficer` |
| 18 | `certificates/view.html` | `Pages/Certificates/View.cshtml` | `_LayoutOfficer` |
| 19 | `reports/participation.html` | `Pages/Reports/Participation.cshtml` | `_LayoutOfficer` |
| 20 | `admin/users.html` | `Pages/Admin/Users.cshtml` | `_LayoutOfficer` |
| 21 | `admin/user-create.html` | `Pages/Admin/UserCreate.cshtml` | `_LayoutOfficer` |
| 22 | `admin/auditlogs.html` | `Pages/Admin/AuditLogs.cshtml` | `_LayoutOfficer` |

---

## 3. Layouts & partials map

Five layouts replace the five prototype shells (plan §5). Active nav state is produced by a **nav tag helper** emitting `aria-current="page"`; in the prototype the same job is done by `Ta.nav` in `assets/app.js` acting on `a[data-nav]`.

| Layout | Prototype shell | Pages | Chrome |
|---|---|---|---|
| `_LayoutPublic` | Public | `index` | Light top nav: logo + AY badge + Door Scanner + Sign In |
| `_LayoutAuth` | Auth | `account/login`, `account/register` | Centered minimal, logo only |
| `_LayoutStudent` | Student | `student/*` (4) | Top nav + student chip + passes badge |
| `_LayoutOfficer` | Officer/Admin | 15 pages (events, masterdata, certificates, reports, approvals, admin) | **Left sidebar** ≥1024px (drawer below) + top bar (role chip, Sign Out) + breadcrumbs |
| `_LayoutKiosk` | Kiosk | `kiosk` | Fullscreen, no nav, ≥56px targets |

**Partials:**

| Partial | Responsibility |
|---|---|
| `_Header` | Top nav / top bar (per layout variant); logo, AY badge, role chip, Sign Out |
| `_SideNav` | Officer/Admin left sidebar — groups **Operations / People / Records** + approvals badge; drawer `<1024px` |
| `_Breadcrumb` | Detail-page breadcrumbs (all detail pages) |
| `_Footer` | Shared footer |
| `_FlashHost` | `TempData` → toast host (prototype: `TaToast`) |
| `_InkSeam` | "The Ink Seam" 160px strip — host `div.ink-seam[data-ink-seam]` + `assets/ink-seam.css` + `assets/ink-seam.js` — **only** `index`, `account/login`, `account/register`, `certificates/view`; static no-JS / reduced-motion fallback; `aria-hidden` |

**Active nav:** tag helper compares `RouteData`/page path → writes `aria-current="page"`. Prototype equivalent: `assets/app.js` `Ta.nav` sets `aria-current` on matching `a[data-nav]`.

---

## 4. Form & handler contract

**Rule:** every flow is a **real form `POST` first**. Markup carries a static `method="post"` + `action` and a `data-action` whose value **mirrors** the future `asp-page-handler` name. `app.js` only enhances — it never replaces the POST.

**Handler map (frozen):**

| `data-action` | Razor handler |
|---|---|
| `account.login` | `OnPostLoginAsync` |
| `account.register` | `OnPostRegisterAsync` |
| `approvals.approve` | `OnPostApproveAsync` |
| `approvals.reject` | `OnPostRejectAsync` |
| `student.rsvp` | `OnPostRsvpAsync` |
| `student.cancel-rsvp` | `OnPostCancelRsvpAsync` |
| `events.save-draft` | `OnPostSaveDraftAsync` |
| `events.publish` | `OnPostPublishAsync` |
| `events.promote` | `OnPostPromoteAsync` |
| `registrations.cancel` | `OnPostCancelRegistrationAsync` |
| `members.save` | `OnPostSaveMemberAsync` |
| `members.toggle-status` | `OnPostToggleMemberStatusAsync` |
| `venues.save` | `OnPostSaveVenueAsync` |
| `eventtypes.add` | `OnPostAddEventTypeAsync` |
| `eventtypes.archive` | `OnPostArchiveEventTypeAsync` |
| `certificates.endorse` | `OnPostEndorseEligibilityAsync` |
| `certificates.issue-batch` | `OnPostIssueBatchAsync` |
| `certificates.issue` | `OnPostIssueAsync` |
| `users.toggle-status` | `OnPostToggleUserStatusAsync` |
| `users.save` | `OnPostSaveUserAsync` |
| `kiosk.session-change` | `OnGetAsync` (query) |
| `kiosk.check-in` | `OnPostCheckInAsync` |

**Prototype wiring status (verified Phase 6, 2026-10-16):** 19 of the 22 handlers exist in the prototype as real form POSTs — 18 as form-level `data-action` and `events.save-draft` as secondary-submit wiring (`data-submit-action` on the Save draft button in `events/create.html`, promoted to the form action by page JS on submit). **Three are target-only** (no prototype form exists):

| `data-action` | Prototype | Port note |
|---|---|---|
| `members.save` | roster is search/filter + status toggle only | add member create/edit form in the port |
| `certificates.endorse` | prototype issues directly from the eligible list | endorsement step is new at port |
| `kiosk.session-change` | read-only live-session chip (`data-ksession`) | event selected via `?eventId=` query → `OnGetAsync` |

**Destructive actions:** marked `[data-confirm]`. Prototype routes them through `Ta.dialog.confirm()` (promise, focus trap, Esc, `aria-modal`). Server-side, the same action becomes a **confirmation POST carrying an anti-forgery token** — the POST is the source of truth; the JS dialog is enhancement only.

---

## 5. localStorage → server swap list

`Ta.store` is the **single swap surface**. Pages never touch `localStorage` directly; every read/write goes through the store, so the swap is a one-layer replacement with EF Core entities.

| Prototype key (`attendta:v2:*`) | Target entity |
|---|---|
| `attendta:v2:members` | `Member` |
| `attendta:v2:users` | `AppUser` |
| `attendta:v2:approvals` | `MembershipRequest` |
| `attendta:v2:events` | `Event` — gains one **`Mood`** property (see §10) |
| `attendta:v2:types` | `EventType` |
| `attendta:v2:venues` | `Venue` |
| `attendta:v2:registrations` | `Registration` |
| `attendta:v2:passes` | `Pass` (**derived**) |
| `attendta:v2:certificates` | `Certificate` |
| `attendta:v2:auditlog` | `AuditLog` |
| `attendta:v2:scans` | `CheckInScan` (door-scan log: code, result, duplicate window) |
| `attendta:v2:session` | auth cookie / claims |
| `attendta:v2:prefs` | `UserPreference` (density, reduced-motion) |
| `attendta:v2:sidebar` | user preference |

---

## 6. Tailwind compile step

**Prototype:** Tailwind **Play CDN** (dev-only; requires `unsafe-eval`) + `assets/tailwind.config.js` as the **single canonical config** replacing the 22 duplicated inline configs (plan findings §1.7).

- Legacy numeric aliases (`ink-950/900/700/500`, `scholastic-500/600/50`) exist **only** for pre-rebuild pages and are **removed at port**.
- `assets/tokens.css` defines the palette as **CSS custom properties**; the config maps utilities to those vars, so one palette serves both stacks.

**Port:**

1. Install Tailwind CLI.
2. `content` = the **Razor views** (`Pages/**/*.cshtml`).
3. Output → `wwwroot/css/site.css`.
4. Design tokens **stay as CSS custom properties** (unchanged from the prototype).
5. `components.css` is **copied as-is** — it is plain CSS with **no `@apply`**, so it compiles without the Tailwind pipeline.

---

## 7. CSP note

- **Dev (prototype):** Tailwind Play CDN mandates `unsafe-eval` in `script-src`; acceptable for local dev only.
- **Production (Razor):** Tailwind is compiled ahead of time, so **strict CSP** can be enforced — no `unsafe-eval`. All scripts are external (`wwwroot/js/app.js`, no inline scripts), inline styles eliminated, and a per-response **nonce** is applied to any remaining inline `<style>`/`<script>`.

---

## 8. Asset & sprite notes

- **Icon sprite** `assets/icons.svg` is loaded over **HTTP** (`<use href=".../icons.svg#id">`); the server must send `image/svg+xml`. **Re-verify MIME** for `wwwroot` static files at port (ASP.NET static file middleware must map `.svg` → `image/svg+xml`). Known risk, plan §13.
- **Logo** `assets/attendTa_logo.jpg` used in headers, pass emblem, kiosk.
- **Media budget:** cover images **≤250KB** each; every `<img>` has explicit `width`/`height`; images **below the fold** load with `loading="lazy"`.
- **Legacy renderer:** `js/qr-engine.js` (prototype-era vector-QR SVG generator) is **not referenced by the rebuilt pages** — do not port it. Passes ship as gate codes; if QR pass images are introduced at port, render them server-side.

---

## 9. Open items

- **Handler wiring** — verified final in Phase 6: 19/22 wired in the prototype, 3 target-only (§4 wiring status). This map's names are frozen.
- **`_InkSeam`** — shipped in the prototype (`assets/ink-seam.css` + `assets/ink-seam.js`; `index`, `account/login`, `account/register`, `certificates/view` only; reduced-motion + no-JS fallbacks). Port as host div + both assets.
- **Kiosk camera** — implemented in `assets/app.js` `Ta.kiosk`: user-gesture camera start (`facingMode: environment`), `jsQR` frame decode (CDN), permission-denied → toast + manual entry. Manual **pass-code or student-number POST** (`kiosk.check-in` → `OnPostCheckInAsync`) is the base flow and fallback.
- **QR pass images** — the prototype prints **gate codes**, not QR images; any QR rendering is a port-side decision (do not port `js/qr-engine.js`; see §8).

---

## 10. Event Moods addendum (UI feature, prototype shipped 2026-10-16)

Live-event student backdrop + Live-Now hero. The whole system is CSS + one entity field — no new routes, no new handlers (plan: `plan.md`).

- **Entity:** `Event.Mood` (string/enum, nullable). Missing/unknown value → server-side type default: 1→drift, 2→bloom, 3→drift, 4→drift, 5→bloom, 6→bloom, 7→bloom, 8→drift (prototype source of truth: `assets/app.js` `Ta.mood.byType`). One trivial EF migration.
- **Rendering:** partial `_EventBackdrop.cshtml` — mood + accent in, markup out:
  `<div class="event-backdrop" aria-hidden="true"><span class="event-backdrop__a"></span><span class="event-backdrop__b"></span></div>`
  plus a `.mood-content` wrapper around the page content. `data-mood` / `data-accent` are **server-rendered** on the page root (Razor: zero flash-of-wrong-mood; the prototype JS-sets them and fades in 240ms). `student/details.html` adds `event-backdrop--quiet`. Backdrops ship **only** on the two student pages — never officer/admin/kiosk/passes/index. While live the page root also carries `data-accent` — **Tier 1 takeover**: the backdrop paints an accent ground wash and the student header gains a 2px inset accent rule (no chrome recolor; same verified accents).
- **Form binding:** the `events/create.html` picker is a plain radio group `name="Mood"` (3 presets — Plain / Drift / Bloom — aria-labelled) inside the existing form — the field rides the current `events.publish` / `events.save-draft` POST and model-binds to `Event.Mood`. Handler map (§4) untouched. The type→mood suggestion is presentation-only (prototype JS; port may keep it or default server-side).
- **CSS:** `components.css` section 30 (backdrops + officer picker chips) copies as-is — plain CSS, no `@apply`, no inline styles; CSP-safe (§7). Guardrails enforced by the prototype checker: F9 (kill-blocks present) + P13 (backdrop only on allowed pages, `aria-hidden`, no inline style, whitelisted mood values).
- **Prefs:** `.mood-frozen` (from `prefs.reducedMotion`, prototype `Ta.mood.applyFreeze`) maps to the `UserPreference` row already in §5; `prefers-reduced-motion` is honored in CSS regardless.
- **Open product calls (plan.md §10):** mood names, per-event accent override, public index, passes texture, published-event editing.
