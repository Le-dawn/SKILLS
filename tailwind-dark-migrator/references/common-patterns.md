# Common dark: Patterns to Variable Mapping

> This reference contains the most frequent `dark:` patterns found in real projects and their corresponding semantic variable replacements. Use this during Step 5-7 of the migration workflow.

## Table of Contents

- [L2 Text Hierarchy](#l2-text-hierarchy)
- [L2 Surface Hierarchy](#l2-surface-hierarchy)
- [L2 Border Hierarchy](#l2-border-hierarchy)
- [L3 Accent Colors](#l3-accent-colors)
- [L3 Accent Hover Colors](#l3-accent-hover-colors)
- [L3 Ring / Focus Colors](#l3-ring--focus-colors)
- [L3 Active/Selected State](#l3-activeselected-state)
- [L3 Badge Colors](#l3-badge-colors)
- [L3 Tag State (PromptPanel style)](#l3-tag-state-promptpanel-style)
- [L3 Gradients](#l3-gradients)
- [L3 Utility Classes](#l3-utility-classes)
- [L3 Focus Ring Offset](#l3-focus-ring-offset)
- [L3 Disabled State](#l3-disabled-state)
- [L3 Scrollbar](#l3-scrollbar)
- [L3 Native Elements](#l3-native-elements)
- [L3 Body Background](#l3-body-background)

---

## L2 Text Hierarchy

| Pattern | Variable | Notes |
|---------|----------|-------|
| `text-zinc-900 dark:text-zinc-100` | `text-heading` | Main titles |
| `text-zinc-700 dark:text-zinc-300` | `text-body` | Body text |
| `text-zinc-600 dark:text-zinc-400` | `text-caption` | Auxiliary text |
| `text-zinc-500 dark:text-zinc-400` | `text-caption` | Auxiliary text (alt) |
| `text-zinc-400 dark:text-zinc-600` | `text-placeholder` | Placeholder/disabled |
| `text-zinc-400 dark:text-zinc-500` | `text-hint` | Secondary hints |
| `text-white dark:text-zinc-950` | `text-inverse` | Inverse text |

## L2 Surface Hierarchy

| Pattern | Variable | Notes |
|---------|----------|-------|
| `bg-white dark:bg-zinc-900` | `bg-surface` | Top-level background |
| `bg-zinc-50 dark:bg-zinc-800` | `bg-elevated` | Card/panel background |
| `bg-zinc-100 dark:bg-zinc-950` | `bg-inset` | Input fields |
| `hover:bg-black/5 dark:hover:bg-white/5` | `hover:bg-surface-hover` | Hover highlight |
| `bg-black/20 dark:bg-white/10` | `bg-overlay` | Overlay/backdrop |

## L2 Border Hierarchy

| Pattern | Variable | Notes |
|---------|----------|-------|
| `border-black/10 dark:border-white/10` | `border-divider` | Standard border |
| `border-black/4 dark:border-white/4` | `border-divider-subtle` | Very subtle border |
| `border-zinc-300 dark:border-zinc-600` | `border-divider-strong` | Emphasized border |

## L3 Accent Colors

| Pattern | Variable | Light | Dark |
|---------|----------|-------|------|
| `text-sky-500 dark:text-sky-400` | `text-accent-sky` | sky-500 | sky-400 |
| `text-teal-500 dark:text-teal-400` | `text-accent-teal` | teal-500 | teal-400 |
| `text-teal-600 dark:text-teal-400` | `text-accent-teal` | teal-600 | teal-400 |
| `text-emerald-500 dark:text-emerald-400` | `text-accent-emerald` | emerald-500 | emerald-400 |
| `text-amber-500 dark:text-amber-400` | `text-accent-amber` | amber-500 | amber-400 |
| `text-red-500 dark:text-red-400` | `text-accent-red` | red-500 | red-400 |
| `text-rose-500 dark:text-rose-400` | `text-accent-rose` | rose-500 | rose-400 |
| `text-orange-500 dark:text-orange-400` | `text-accent-orange` | orange-500 | orange-400 |
| `text-indigo-500 dark:text-indigo-400` | `text-accent-indigo` | indigo-500 | indigo-400 |
| `text-yellow-500 dark:text-yellow-400` | `text-accent-yellow` | yellow-500 | yellow-400 |
| `text-green-500 dark:text-green-400` | `text-accent-green` | green-500 | green-400 |
| `text-green-600 dark:text-green-400` | `text-accent-green` | green-600 | green-400 |

## L3 Accent Hover Colors

| Pattern | Variable | Light | Dark |
|---------|----------|-------|------|
| `hover:text-sky-500 dark:hover:text-sky-400` | `hover:text-accent-sky` | sky-500 | sky-400 |
| `hover:text-teal-600 dark:hover:text-teal-300` | `hover:text-accent-teal` | teal-600 | teal-300 |
| `hover:text-red-600 dark:hover:text-red-300` | `hover:text-accent-red` | red-600 | red-300 |

## L3 Ring / Focus Colors

| Pattern | Variable | Light | Dark |
|---------|----------|-------|------|
| `ring-sky-500 dark:ring-sky-400` | `ring-accent-sky` | sky-500 | sky-400 |

## L3 Active/Selected State

| Pattern | Variables | Light | Dark |
|---------|-----------|-------|------|
| `bg-teal-500/10 dark:bg-teal-500/20` | `bg-option-active-bg` | teal-500/10 | teal-500/20 |
| `border-teal-500/50` (no dark:) | `border-option-active-border` | teal-500/50 | same |
| `text-teal-600 dark:text-teal-300` | `text-option-active-text` | teal-600 | teal-300 |
| `shadow-[0_0_12px_rgba(20,184,166,0.1)] dark:shadow-[0_0_12px_rgba(20,184,166,0.15)]` | `shadow-option-active-shadow` | teal-500/10 | teal-500/15 |

## L3 Badge Colors

| Pattern | Variable | Light | Dark |
|---------|----------|-------|------|
| `text-sky-700 dark:text-sky-100` | `text-badge-sky-text` | sky-700 | sky-100 |
| `text-amber-700 dark:text-amber-100` | `text-badge-amber-text` | amber-700 | amber-100 |
| `text-red-700 dark:text-red-100` | `text-badge-red-text` | red-700 | red-100 |
| `text-rose-700 dark:text-rose-100` | `text-badge-rose-text` | rose-700 | rose-100 |

## L3 Tag State (PromptPanel style)

| Pattern | Variables | Light | Dark |
|---------|-----------|-------|------|
| `bg-teal-50 border-teal-200 text-teal-700` | `bg-tag-active-bg border-tag-active-border text-tag-active-text` | teal-50/teal-200/teal-700 | teal-600/20 / teal-500/40 / teal-300 |
| `dark:bg-teal-600/20 dark:border-teal-500/40 dark:text-teal-300` | (same as above) | | |
| `hover:bg-teal-100 dark:hover:bg-teal-600/30` | `hover:bg-tag-active-hover-bg` | teal-100 | teal-600/30 |
| `bg-sky-50 border-sky-200 text-sky-700` | `bg-tag-sky-active-bg border-tag-sky-active-border text-tag-sky-active-text` | sky-50/sky-200/sky-700 | sky-500/20 / sky-500/30 / sky-400 |

## L3 Gradients

| Pattern | Variables | Light | Dark |
|---------|-----------|-------|------|
| `from-red-50 to-white dark:from-red-950/10 dark:to-slate-900` | `from-alert-urgent-from to-alert-urgent-to` | red-50/white | red-950/10 / slate-900 |
| `from-amber-50 to-white dark:from-amber-950/10 dark:to-slate-900` | `from-alert-important-from to-alert-important-to` | amber-50/white | amber-950/10 / slate-900 |
| `from-sky-50 to-white dark:from-sky-950/10 dark:to-slate-900` | `from-alert-warning-from to-alert-warning-to` | sky-50/white | sky-950/10 / slate-900 |
| `from-zinc-200/80 to-zinc-100/80 dark:from-zinc-900/80 dark:to-zinc-950/80` | `from-overlay-from to-overlay-to` | zinc-200/80 / zinc-100/80 | zinc-900/80 / zinc-950/80 |
| `bg-[radial-gradient(...,rgba(203,213,225,0.4)_100%)] dark:bg-[radial-gradient(...,rgba(15,23,42,0.6)_100%)]` | `bg-[radial-gradient(...,var(--ambient-to)_100%)]` | slate-300/40 | slate-900/60 |

## L3 Utility Classes

| Pattern | Variables | Light | Dark |
|---------|-----------|-------|------|
| `bg-white/60 dark:bg-slate-900/40` + `border-slate-300/50 dark:border-slate-700/50` | `bg-glass-bg border-glass-border` | white/60 / slate-300/50 | slate-900/40 / slate-700/50 |
| `hover:shadow-[0_0_20px_rgba(6,182,212,0.15)] dark:hover:shadow-[0_0_20px_rgba(6,182,212,0.3)]` | `shadow-glow-hover-shadow` | cyan-500/15 | cyan-500/30 |
| `hover:border-cyan-500/30 dark:hover:border-cyan-500/50` | `border-glow-hover-border` | cyan-500/30 | cyan-500/50 |
| `hover:bg-slate-100/60 dark:hover:bg-slate-800/60` | `bg-glow-hover-bg` | slate-100/60 | slate-800/60 |

## L3 Focus Ring Offset

| Pattern | Variable | Light | Dark |
|---------|----------|-------|------|
| `ring-offset-white dark:ring-offset-zinc-900` | `ring-offset-ring-offset` | white | zinc-900 |
| `focus-visible:ring-offset-white dark:focus-visible:ring-offset-zinc-900` | `focus-visible:ring-offset-ring-offset` | white | zinc-900 |

## L3 Disabled State

| Pattern | Variable | Light | Dark |
|---------|----------|-------|------|
| `text-zinc-300 dark:text-zinc-700` | `text-disabled` | zinc-300 | zinc-700 |

## L3 Scrollbar

| Pattern | Variable | Light | Dark |
|---------|----------|-------|------|
| `scrollbar-color: rgba(0,0,0,0.2) transparent` | `scrollbar-color: var(--scrollbar-thumb) transparent` | black/20 | white/12 |
| `::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.2) }` | `background: var(--scrollbar-thumb)` | black/20 | white/12 |
| `.dark ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12) }` | (use same var) | | |

## L3 Native Elements

| Pattern | Variable | Light | Dark |
|---------|----------|-------|------|
| `option { background-color: #ffffff; color: #18181b; }` | `background-color: var(--option-bg); color: var(--option-text);` | white / zinc-900 | zinc-900 / zinc-200 |
| `.dark option { background-color: #18181b; color: #e4e4e7; }` | (use same var) | | |

## L3 Body Background

| Pattern | Variable | Light | Dark |
|---------|----------|-------|------|
| `:root:not(.dark) body { background-color: #f1f5f9; ... }` | `background-color: var(--body-bg);` | slate-100 | #0b1120 |
| `.dark body { background-color: #0b1120; ... }` | (use same var) | | |
