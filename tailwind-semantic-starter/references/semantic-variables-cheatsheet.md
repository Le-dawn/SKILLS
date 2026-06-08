# Semantic Variables Cheatsheet

Quick reference for semantic CSS variables. Use this when writing or reviewing component code.

> **Rule of thumb**: If you find yourself typing a color name (zinc, slate, gray, white, black), stop and use a semantic variable instead.

> ⚠️ **颜色值仅为示例默认值**：本表 Light / Dark 列中的颜色（如 zinc-900、zinc-100）基于默认 zinc 中性色调。
> 实际项目中 `:root` / `.dark` 的变量赋值必须来自**项目自身的色彩体系**，不得直接照搬本表。
> 新建空项目可使用这些默认值；已有项目需先用 Step 1.5 提取现有色彩后再赋值。

---

## L2 Text Hierarchy (Most Used)

| Variable | Light | Dark | Usage |
|----------|-------|------|-------|
| `text-heading` | zinc-900 | zinc-100 | Page titles, card titles, bold labels |
| `text-body` | zinc-700 | zinc-300 | Body paragraphs, descriptions |
| `text-caption` | zinc-500 | zinc-400 | Auxiliary text, metadata |
| `text-hint` | zinc-400 | zinc-500 | Secondary hints, placeholders |
| `text-placeholder` | zinc-400 | zinc-600 | Form placeholders, disabled hints |
| `text-inverse` | white | zinc-950 | Text on colored backgrounds |

**Frequency**: `heading` > `body` > `caption` > `hint` > `placeholder` > `inverse`

---

## L2 Surface Hierarchy (Most Used)

| Variable | Light | Dark | Usage |
|----------|-------|------|-------|
| `bg-surface` | white | zinc-900 | Top-level background, cards |
| `bg-elevated` | zinc-50 | zinc-800 | Slightly raised surfaces |
| `bg-inset` | zinc-100 | zinc-950 | Input fields, nested areas |
| `bg-overlay` | black/40 | black/60 | Modal backdrops, overlays |
| `hover:bg-surface-hover` | black/5 | white/5 | Hover state backgrounds |

**Frequency**: `surface` > `elevated` > `inset` > `surface-hover` > `overlay`

---

## L2 Border Hierarchy (Most Used)

| Variable | Light | Dark | Usage |
|----------|-------|------|-------|
| `border-divider` | zinc-200 | white/10 | Standard borders, separators |
| `border-divider-subtle` | zinc-100 | white/5 | Very subtle borders |
| `border-divider-strong` | zinc-300 | white/20 | Emphasized borders |

**Frequency**: `divider` > `divider-subtle` > `divider-strong`

---

## L3 Accent Colors

| Variable | Light | Dark | Usage |
|----------|-------|------|-------|
| `text-accent-sky` | sky-500 | sky-400 | Info, links, primary actions |
| `text-accent-teal` | teal-600 | teal-400 | Success, active states |
| `text-accent-emerald` | emerald-500 | emerald-400 | Positive indicators |
| `text-accent-amber` | amber-500 | amber-400 | Warnings, attention |
| `text-accent-red` | red-500 | red-400 | Errors, alerts |
| `text-accent-rose` | rose-500 | rose-400 | Destructive actions |
| `text-accent-orange` | orange-500 | orange-400 | Warnings (alt) |
| `text-accent-indigo` | indigo-500 | indigo-400 | Secondary brand |
| `text-accent-yellow` | yellow-500 | yellow-400 | Highlights |
| `text-accent-green` | green-500 | green-400 | Success (alt) |

> All accent colors also work with `bg-*` and `border-*` prefixes.

---

## L3 Active / Selected State

| Variable | Light | Dark | Usage |
|----------|-------|------|-------|
| `bg-option-active-bg` | teal-500/10 | teal-500/20 | Selected item background |
| `border-option-active-border` | teal-500/50 | teal-500/50 | Selected item border |
| `text-option-active-text` | teal-600 | teal-300 | Selected item text |
| `shadow-option-active-shadow` | teal glow/10 | teal glow/15 | Selected item glow |

---

## L3 Badge Text Colors

| Variable | Light | Dark | Usage |
|----------|-------|------|-------|
| `text-badge-sky-text` | sky-700 | sky-100 | Sky badge text |
| `text-badge-amber-text` | amber-700 | amber-100 | Amber badge text |
| `text-badge-red-text` | red-700 | red-100 | Red badge text |
| `text-badge-rose-text` | rose-700 | rose-100 | Rose badge text |

---

## L3 Utility Classes

| Class | Effect |
|-------|--------|
| `glass-panel` | Frosted glass background + border |
| `glow-hover` | Subtle glow on hover |
| `alert-pulse` | Red pulse animation |

---

## L3 Misc Variables

| Variable | Light | Dark | Usage |
|----------|-------|------|-------|
| `ring-offset-[var(--ring-offset)]` | white | zinc-900 | Focus ring offset (v4 uses arbitrary value) |
| `text-disabled` | zinc-300 | zinc-700 | Disabled text |

---

## Quick Decision Tree

```
Need a color?
├── Text on a surface?
│   ├── Main title/label → text-heading
│   ├── Body paragraph → text-body
│   ├── Auxiliary info → text-caption
│   ├── Secondary hint → text-hint
│   └── Placeholder → text-placeholder
├── Background?
│   ├── Top-level page/card → bg-surface
│   ├── Raised element → bg-elevated
│   ├── Input field → bg-inset
│   └── Hover state → hover:bg-surface-hover
├── Border?
│   ├── Standard separator → border-divider
│   ├── Very subtle → border-divider-subtle
│   └── Emphasized → border-divider-strong
├── Emphasis / Status?
│   ├── Info/primary → accent-sky
│   ├── Success → accent-teal / accent-emerald
│   ├── Warning → accent-amber
│   ├── Error/alert → accent-red
│   └── Destructive → accent-rose
└── Special effect?
    ├── Frosted glass → glass-panel
    └── Hover glow → glow-hover
```
