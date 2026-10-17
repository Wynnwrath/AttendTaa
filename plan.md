# AttendTa v2 — UI Improvements Plan · "Event Moods" & Live Backdrop

**Status:** implemented in the prototype (UI-0.5 → UI-4, 2026-10-16; final cut to Plain / Drift / Bloom + Tier 1 live takeover, 2026-10-17) — see §10 for what remains open · Companion to `IMPLEMENTATION_PLAN.md` §12 (this formalizes the deferred *"full-site live event takeover"*)
**Date:** 2026-10-16 · **Rev:** 2 (skill-verified design fit + preview phase added)
**Scope:** student-facing pages only · prototype-first (build in `v2/`, then port mechanically per `RAZOR-PORT.md`)

---

## 1. The idea, sharpened

Your concept: the current live event repaints the student experience — a large "happening now" card plus an ambient page background whose **shape/motion ("mood")** and **color** come from the event, chosen by the officer when creating it.

Translation into this project's system — three deliberate splits keep it from becoming slop:

1. **Mood vs. accent.** *Mood* = shape & motion (waves, grid, bloom…). *Accent* = color. Color is **already solved**: each event type carries one of 8 contrast-verified accent families (`tokens.css`). The officer picks the **mood**; the color follows the **type** — no free-form colors, ever.
2. **Ambient vs. hero.** The backdrop is ambient (viewport ground). The **Live Now hero card** on `student/events` is the single *signature moment* — the only place the mood runs at full expression (design rule: reserve impact for punctuation; everything else stays quiet and contained).
3. **Presets only.** A small closed set — final: Plain / Drift / Bloom (Lattice, Ember and Tempo were built, previewed, then retired). No officer uploads, no arbitrary gradients. This is what keeps the review bar and the port tractable.

**Naming note:** this project reserves "theme" for dark/light (deferred §12). Call this **Event Moods** to avoid collision.

---

## 2. Current state (what already exists)

| Building block | Where | Reused as |
|---|---|---|
| 8 accent families (base/deep/subtle/glow) | `tokens.css`, register in `DESIGN-TOKENS.md` §Event accents | Mood **color** source — zero new color values |
| Type → accent mapping (Seminar→indigo, Recognition→amber, Workshop→teal, Assembly→slate, Outreach→moss, Sports→orange, Cultural Night→violet, Orientation→crimson) | `app.js` types seed:121–130 | Mood **defaults** follow the same mapping |
| `status === 'live'` detection + `data-live-banner` band | `app.js:1218`, `student/events.html:68–79` | Upgraded into the Live Now hero |
| Ink Seam (SVG wave strip, reduced-motion + no-JS fallbacks) | `assets/ink-seam.css/.js`, 4 pages | Proven precedent for decorative, constrained motion |
| Accent scoping rule — *never* on nav/admin/buttons/status/certificates | `DESIGN-TOKENS.md` locked rules | Extends cleanly: backdrops are **student pages only** |

---

## 3. The mood set (closed — ships as CSS, no assets)

All moods: pure CSS/SVG layers, 2–3 DOM nodes max, opacity ≤ 14% over `--canvas-ground`, colors drawn **only** from the event's accent variables (`--event-{family}`, `-subtle`, `-glow`). No `filter: blur()` (expensive on mobile) — soft edges via radial-gradients. `pointer-events: none`, `aria-hidden="true"`, `position: fixed; inset: 0; z-index: 0` behind an opaque content wrapper.

| Mood | Character | Technique | Default for types |
|---|---|---|---|
| **Plain** | none (today's look) | — | — |
| **Drift** | slow layered waves, editorial calm | 2 oversized wave layers, `translateX` loop 40–60s | Seminar, Workshop, Assembly, Orientation |
| **Bloom** | soft overlapping translucent orbs | 4–5 radial-gradient circles, slow scale/translate 30s | Outreach, Sports, Recognition, Cultural Night |

**Final cut (2026-10-17):** Lattice, Ember and Tempo were retired after visual review — one texture mood (Bloom) + one motion mood (Drift) keep the set restrained.

**Static freeze-frame:** every mood has a defined reduced-motion/no-JS state — the same composition, unanimated. Moods must look intentional when frozen; if one only works in motion, it's cut.

**Print rule:** `@media print { .event-backdrop { display: none } }` — passes, certificates, reports never print a backdrop.

---

## 4. Skill-verified design fit & calibration

Checked against workspace skills (`design-thinking`, `design-taste-frontend`, `frontend-state-theme`, `frontend-animation`). Verdict: **feasible — and the moods map to patterns the design skills explicitly recognize.** This is a refinement of an established language, not a new invention.

**Mood ↔ recognized pattern**

| Mood | Recognized pattern | Notes from the skills |
|---|---|---|
| Drift | layered wave fields | Ink Seam is the in-project precedent; decorative-only, freezing cleanly |
| Lattice | static grid + "breathing" nodes | breathing status indicator is a sanctioned micro-interaction |
| Bloom | mesh-gradient blobs | named as a premium background archetype (organic, lava-lamp) |
| Ember | sparse particle drift | particle-lite: ≤ 8 nodes, DOM-only (no canvas) |
| Tempo | kinetic band / sweep | a single moving highlight layer only |

*The Lattice / Ember / Tempo rows record the initial candidate calibration — the final cut keeps Drift + Bloom (see §3).*

**Calibration (locked)**

- Motion class: **fluid CSS** — `transform`/`opacity` only; entrance fade + 8px rise, 240ms (`--motion-slow`), `--ease-standard`; loops 20–60s, ease-in-out, seamless. No JS, no canvas, no libraries.
- Opacity: layers 8–14% over `--canvas-ground`; glow halos ≤ 12%.
- Layer budget: ≤ 3 layers; below 768px only the calmest single layer animates; reduced-motion → full freeze-frame.
- Texture guard: any grain/noise lives on a `position: fixed; pointer-events: none` layer — never on scrolling content.
- Z-scale: backdrop sits under the content wrapper at page level; the systemic tokens (`--z-nav` 30+) stay untouched.
- The Live Now hero is the page's **single elevated surface** — elevation is what grants it the one big moment; everything else stays hairline/flat.

**Rejected from the skills (stack mismatch or project conventions win):** React tooling (Framer / GSAP / ThreeJS), spring physics, generic motion-intensity defaults, glass/neon treatments — the frozen tokens and Institutional Precision rules govern wherever they differ.

---

## 5. Where it appears (student side only)

| Page | Treatment |
|---|---|
| `student/events.html` | **Full ambient backdrop** + **Live Now hero** (upgrade of the existing live band): large card — accent gauge, event title/type badge, venue + time, live pulse, time-remaining, CTAs (View details · Show pass). No live event → hero falls back to next upcoming; no events → neutral empty state |
| `student/details.html` | Ambient backdrop, quieter (mood at lower opacity, dossier header rule carries accent as today) |
| `student/history.html` | Header band tint only — no full backdrop |
| `student/passes.html` | **No backdrop** — pass must print clean; unchanged (open question Q4) |
| `index.html` (public) | Unchanged (existing LIVE band mirrors status without mood) — open question Q3 |
| officer / admin / kiosk / approvals / certificates | **Never.** Kiosk stays sober dark; console stays Institutional |

---

## 6. Officer flow (where moods are set)

- `events/create.html`: new **"Mood" field** after Cover — radio-card row (3 options: Plain / Drift / Bloom) with tiny CSS previews and a *"shown to students only while this event is live"* helper. Default = suggested by selected Type; officer may change. No new handler: the field rides the existing `events.publish` / `events.save-draft` POST (`Mood` form field). Draft-edit on the same page already works (`data-label-edit`), so moods are editable while an event is a draft.
- Published-event editing: **out of scope v1** (open question Q5).
- Store: `events` collection gains `mood` (string). Missing `mood` → code falls back to the type's default mood (backward compatible — no migration needed). Two seed events get explicit moods for demo.

---

## 7. Razor Pages / ASP.NET C# feasibility — verdict: **easy, and port-friendly**

Why this is a low-risk feature on Razor:

- **Data:** `Event` entity gains one `Mood` property (string/enum). One trivial EF migration.
- **Rendering:** server-side attribute — `<div class="event-backdrop" data-mood="drift" aria-hidden="true">` + `data-accent` on the wrapper. A tiny partial `_EventBackdrop.cshtml` (mood + accent in, markup out). **Zero client JS** for the static case; the whole system is CSS.
- **CSP:** fully compatible — no inline styles, no inline scripts; layer composition via classes/pseudo-elements in `components.css` (which the port copies as-is — it has no `@apply`).
- **Handler map:** untouched — no new `data-action`; `Mood` binds via normal model binding on the existing handlers. Frozen routes untouched.
- **Performance:** `transform`/`opacity` only, long durations, no rAF/canvas/JS loops; `prefers-reduced-motion` → static; backdrops are single fixed layers (no scroll work → no jank).
- **A11y:** decorative layers `aria-hidden`; all text stays on opaque surfaces (cards/veils) so every existing contrast pair remains valid; LIVE pulse stays < 3 Hz.
- **Note:** the loaded animation tooling (ReactBits / motion.dev) does **not** apply — this is a zero-build vanilla + Razor stack. CSS/SVG-only is both the right aesthetic and what keeps the port mechanical.
- **Applying the mood:** rides the project's existing data-attribute convention (`data-density`, `data-accent`) — `data-mood` on the page root, styles scoped in CSS. Prototype: mood is read from the store and the backdrop fades in only once ready (240ms; instant under reduced-motion) so there is no flash-of-wrong-mood; Razor: the attribute is server-rendered → zero flash by construction. App-level `prefs.reducedMotion` also forces freeze-frames on top of the media query.

**Guardrails (enforced by the checker in UI-1):** mood whitelist, backdrop only on allowed student pages, `aria-hidden` present, no inline `style=`, reduced-motion and print kill-blocks present in `components.css`.

---

## 8. Phases

| Phase | Work | Gate |
|---|---|---|
| **UI-0** | Approve this plan + resolve open questions | user sign-off |
| **UI-0.5** | **Visual preview** — disposable page rendering all 6 moods on the real Live-Now hero with a mood/accent switcher, so you can see the look before production CSS lands. Scratch-only: deleted before any checker run (same policy as the probe rigs) | your visual approval |
| **UI-1** | Backdrop system in `components.css` (5 moods + Plain, freeze-frames, print/reduced-motion guards) + checker rules | checker pass; screenshots of all moods × (indigo/amber/moss) |
| **UI-2** | Live Now hero + ambient backdrop on `student/events`; backdrop on `student/details` | 390px probe, keyboard pass, screenshot review vs review bar |
| **UI-3** | Mood field on `events/create.html` + type-default mapping in `store` + demo seed moods | create → publish → student-view trace |
| **UI-4** | Perf/motion/contrast audit; docs: `DESIGN-TOKENS.md` gains an *Event Moods* register section; `RAZOR-PORT.md` gains `Event.Mood` + `_EventBackdrop` notes; README blurb | full checker + design review |

---

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Design slop / "toy" feel | Closed set of 3 restrained presets (Plain / Drift / Bloom); Institutional naming; opacity ≤ 14%; one signature moment (hero) |
| Contrast regressions | Backdrop behind opaque surfaces only; colors from pre-verified accent tokens |
| Mobile perf / battery | Transform/opacity only, no blur, ≤ 3 layers, long durations, static under reduced-motion |
| Motion sensitivity | Mandatory freeze-frames; global reduced-motion honored |
| Print contamination | `@media print` kill-block + passes get no backdrop at all |
| Scope creep (officer "design studio") | Presets only; accent stays type-owned v1 |
| Port drift | Everything is CSS classes + one entity field; no new handlers/routes |

---

## 10. Open questions (need your call before UI-1)

1. **Mood names** — **resolved 2026-10-17:** final set Plain / Drift / Bloom (Lattice, Ember and Tempo retired after visual review).
2. **Per-event accent override** — v1 keeps color strictly type-owned (recommended). Add override later, or now?
3. **Public `index.html`** — keep neutral (recommended), or show the live event's mood there too?
4. **Passes** — keep print-clean no-backdrop (recommended), or give the pass strip a mood texture?
5. **Editing** — moods changeable after publish (needs an edit flow later), or draft-only for v1?
6. **Default mapping table** (§3) — **resolved:** formal types → Drift; celebratory/community types → Bloom.
