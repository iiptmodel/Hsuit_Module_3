# MediScan AI — Frontend Overhaul Design Spec

**Date:** 2026-06-24  
**Approach:** A — "Warm Studio" (full front-end rebuild, warm & approachable aesthetic)  
**Scope:** `chat.html`, `chat.css`, `chat.js` — no backend changes

---

## 1. Design Tokens

### Color Palette

All tokens defined on `:root` and overridden by `:root[data-theme="dark"]`.

| Token | Light | Dark |
|---|---|---|
| `--ground` | `#F7F5F0` | `#1A1814` |
| `--surface` | `#FFFFFF` | `#242017` |
| `--surface-2` | `#F2EFE9` | `#2D2921` |
| `--surface-3` | `#EAE6DE` | `#363028` |
| `--accent` | `#5B8A6F` | `#5B8A6F` |
| `--accent-dim` | `rgba(91,138,111,0.10)` | `rgba(91,138,111,0.14)` |
| `--accent-border` | `rgba(91,138,111,0.25)` | `rgba(91,138,111,0.28)` |
| `--accent-glow` | `rgba(91,138,111,0.18)` | `rgba(91,138,111,0.18)` |
| `--text` | `#2C2319` | `#EDE8DF` |
| `--text-dim` | `#5C4D3C` | `#B8A898` |
| `--text-muted` | `#8C7B6B` | `#7A6B5D` |
| `--border` | `rgba(44,35,25,0.08)` | `rgba(255,255,255,0.07)` |
| `--divider` | `rgba(44,35,25,0.04)` | `rgba(255,255,255,0.04)` |
| `--amber` | `#C8913A` | `#C8913A` |
| `--amber-dim` | `rgba(200,145,58,0.12)` | `rgba(200,145,58,0.12)` |
| `--success` | `#3DAB7B` | `#3DAB7B` |
| `--error` | `#E05555` | `#E05555` |
| `--shadow-sm` | `0 2px 8px rgba(44,35,25,0.07)` | `0 2px 8px rgba(0,0,0,0.40)` |
| `--shadow-md` | `0 6px 20px rgba(44,35,25,0.09)` | `0 6px 20px rgba(0,0,0,0.50)` |
| `--shadow-lg` | `0 16px 36px rgba(44,35,25,0.11)` | `0 16px 40px rgba(0,0,0,0.60)` |

### Typography

- UI font: `DM Sans` (kept — humanist, warm)
- Mono font: `IBM Plex Mono` — used only for timestamps, status badges, file sizes, inline code
- Assistant message body: `DM Sans`, not mono
- Heading weights: 700–800
- Body: 400–500

### Radii & Motion

Unchanged from existing design system (`--r-xs` through `--r-full`, existing easings).

Message entrance animation slowed slightly: `200ms` (was `180ms`) for a more settled feel.

---

## 2. Layout & Structure

### Top Bar (Dashboard Header)

- Height reduced: `44px` (was ~56px)
- Same logo section (icon + title + tagline)
- Stats chips stay but more compact (labels hidden below `1100px` unchanged)
- Theme toggle moves to **sidebar footer** — removed from header
- Header becomes: `[logo] ··· [stats grid]` — clean, slim

### Two-Panel Container

- Grid: `248px sidebar + 1fr main` — unchanged
- `margin: 0.625rem` (tightened from `0.75rem`) for slightly more chat room
- Border-radius: `--r-lg` (unchanged)

### Mobile

- Sidebar hidden at `≤768px`
- Hamburger icon added to chat header (mobile only) — opens sidebar as full-height drawer overlay
- Drawer closes on backdrop tap or Escape

---

## 3. Sidebar

### Header

- "SESSIONS" label (0.65rem, uppercase, muted)
- "New Chat" button: full-width sage pill, weight 700

### Session Items

- Hover: `--surface-2` background + `1px` border (`--border`)
- Active: `--accent-dim` background + `3px` left border in `--accent` + title color `--accent`
- Content: title (ellipsis), preview (ellipsis, muted), timestamp (mono, muted)

### Empty State

- Centered SVG icon (simple medical cross or stethoscope, sage green, 40px)
- Heading: "No sessions yet" (`0.875rem`, weight 600)
- Sub: "Upload a document or ask a question to get started" (muted, `0.8rem`)

### Footer

- Single row: theme toggle (icon button) + `MediScan AI` label + version tag (`0.1`)
- Pinned to bottom of sidebar

---

## 4. Welcome Screen

- Icon: `80px` rounded square, sage-dim background, sage border, sage SVG cross
- `h2`: `2rem`, weight 800, warm near-black, letter-spacing `-0.5px`
- Subtitle: `1rem`, muted, line-height `1.65`
- Feature cards: 2-column grid; each card has a small sage icon (top-left), bold title, muted description
- Quick-start section: sage-bordered card, sage `h3`, muted paragraph, sage primary button
- Mobile: feature cards collapse to 1 column

---

## 5. Chat Header (Per Session)

- Left: session title (ellipsis) + "Active" status pill (pulsing dot) + lang badge
- Right: rename icon + delete icon + files icon
- All unchanged structurally; styled with warm borders/hover states
- Mobile: hamburger icon added to left side of header

---

## 6. Message Bubbles

### User Messages

- Background: `--accent` (sage green)
- Text: `--ground` (warm near-white)
- `border-bottom-right-radius: var(--r-xs)` — asymmetric bubble tail
- Font: `DM Sans`, `0.9rem`, weight 500

### Assistant Messages

- Background: `--surface` (white / dark surface)
- Left border: `3px solid var(--accent-border)` — blockquote-style
- Border: `1px solid var(--border)`
- Font: `DM Sans`, `0.9rem`, line-height `1.72` — **not monospace**
- Markdown rendered (see §8)

### Avatars

- Replace emoji with colored initials circles (`30px`, `border-radius: 50%`)
- User: `U` on `--accent-dim` background, `--accent-border` border
- Assistant: `M` on `--amber-dim` background, amber border — warm, distinct from user
- Font: `DM Sans`, `0.75rem`, weight 700

### Timestamps

- Hidden by default; appear on `.message:hover` via CSS `opacity` transition
- `0.68rem`, mono, `--text-muted`

### Streaming Cursor

- Unchanged (`▋`, blink animation, accent color)

---

## 7. Input Composer

### Default State (single row)

```
[📎 attach] [file chip?] [textarea flex:1] [⚙ options] [▶ send]
```

- Attach button: `38px`, warm border, sage on hover
- Textarea: same styling as current, warm border
- Options toggle (`⚙`): `38px` icon button — toggles the options tray
- Send button: sage green, same sizing

### Options Tray (collapsible row above input)

- Slides in/out with `max-height` transition (`0 → 44px`, `200ms`)
- Contains: Audience pill select + Language pill select
- State persisted in `localStorage` key `mediscan-options-open`
- Default: open (first visit), so users discover the controls

### Drag-and-Drop

- Dropping a file anywhere on `.chat-main` triggers a full-overlay drop zone
- Overlay: `inset: 0`, sage dashed border (`3px dashed var(--accent)`), `backdrop-filter: blur(2px)`
- Label: large sage SVG upload icon + "Drop to attach"
- `dragenter` / `dragleave` / `drop` events on `.chat-main`

---

## 8. Markdown Rendering

Pure JS function, no external dependencies. Replaces `formatMessageContent()`.

Supports (in order, applied via regex chain):

1. `### text` → `<h3>`
2. `## text` → `<h2>`
3. `# text` → `<h1>`
4. `**text**` → `<strong>`
5. `*text*` or `_text_` → `<em>`
6. `` `code` `` → `<code>` (mono font, surface-2 background, accent border)
7. Consecutive lines starting with `- ` or `* ` → wrapped in a single `<ul>`, each line a `<li>`
8. Consecutive lines starting with `\d+. ` → wrapped in a single `<ol>`, each line a `<li>`
9. Blank line → paragraph break (`<p>` wrapping)
10. Remaining `\n` → `<br>`

XSS note: raw HTML in content is escaped before markdown parsing (replace `<` with `&lt;`, `>` with `&gt;`).

---

## 9. Files Panel (Drawer)

- Unchanged structure; styled with warm palette
- File status badges: warm amber for "processing", sage for "done", error red for "error"

---

## 10. Modals & Toasts

### Modals

- Backdrop: `rgba(44,35,25,0.40)` (warmer than current `rgba(0,0,0,0.45)`)
- Modal surface: `--surface`, `--r-xl` border-radius
- Animations: unchanged (scale + translateY)

### Toasts

- Move from bottom-right to **bottom-center**
- `left: 50%; transform: translateX(-50%)`
- Max-width: `380px`
- Entrance: `translateY(8px) → 0` (was `translateX(10px) → 0`)

---

## 11. Accessibility & Responsive

- All existing ARIA attributes preserved (roles, aria-hidden, aria-label, aria-live)
- Focus styles: `2px solid var(--accent)` with `2px offset` on all interactive elements
- `@media (prefers-reduced-motion)` block preserved
- Mobile hamburger button: aria-expanded, aria-controls pointing to sidebar
- Sidebar drawer (mobile): focus trapped while open, Escape closes it

---

## 12. Files Changed

| File | Change |
|---|---|
| `app/templates/chat.html` | Full rewrite — new structure for input composer (options tray), avatar circles, sidebar footer, mobile hamburger, drop zone overlay |
| `app/static/css/chat.css` | Full rewrite — new token system, all component styles |
| `app/static/js/chat.js` | Rewrite `formatMessageContent()` → markdown renderer; add options tray toggle + localStorage persistence; add drag-and-drop handlers; add mobile sidebar drawer; update `displayMessage()` for new avatar markup and timestamp-on-hover |

`app/static/css/style.css` and `app/static/js/app.js` are untouched (they serve a different page).

---

## 13. What Is Not Changing

- All API endpoint calls (`/api/v1/chat/...`, `/api/v1/reports/...`)
- WebSocket logic (setup, reconnect, delta handling)
- Session CRUD (create, load, rename, delete)
- File upload validation (types, size limit)
- Audio polling logic
- All accessibility live regions and screen reader announcements
- `style.css` / `app.js` (different page)
