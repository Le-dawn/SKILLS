# Tailwind CSS v4 Setup Guide

For Tailwind v4 projects, configuration is CSS-first via `@theme inline` in the global CSS file.

## 1. Global CSS File (e.g., `src/index.css`)

```css
@import "tailwindcss";

@custom-variant dark (&:is(.dark *));

@theme inline {
  /* L2 Semantic text colors */
  --color-heading: var(--heading);
  --color-body: var(--body);
  --color-caption: var(--caption);
  --color-hint: var(--hint);
  --color-placeholder: var(--placeholder);
  --color-inverse: var(--inverse);
  /* L2 Semantic surface colors */
  --color-surface: var(--surface);
  --color-surface-hover: var(--surface-hover);
  --color-surface-faint: var(--surface-faint);
  --color-elevated: var(--elevated);
  --color-inset: var(--inset);
  --color-overlay: var(--overlay);
  /* L2 Semantic border colors */
  --color-divider: var(--divider);
  --color-divider-subtle: var(--divider-subtle);
  --color-divider-strong: var(--divider-strong);
  /* L3 Accent colors */
  --color-accent-sky: var(--accent-sky);
  --color-accent-teal: var(--accent-teal);
  --color-accent-emerald: var(--accent-emerald);
  --color-accent-amber: var(--accent-amber);
  --color-accent-red: var(--accent-red);
  --color-accent-rose: var(--accent-rose);
  --color-accent-orange: var(--accent-orange);
  --color-accent-indigo: var(--accent-indigo);
  --color-accent-yellow: var(--accent-yellow);
  --color-accent-green: var(--accent-green);
  /* L3 Active/selected state */
  --color-option-active-bg: var(--option-active-bg);
  --color-option-active-border: var(--option-active-border);
  --color-option-active-text: var(--option-active-text);
  --color-option-active-shadow: var(--option-active-shadow);
  /* L3 Badge text colors */
  --color-badge-sky-text: var(--badge-sky-text);
  --color-badge-amber-text: var(--badge-amber-text);
  --color-badge-red-text: var(--badge-red-text);
  --color-badge-rose-text: var(--badge-rose-text);
  /* L3 Glass/glow utilities */
  --color-glass-bg: var(--glass-bg);
  --color-glass-border: var(--glass-border);
  --color-glow-hover-bg: var(--glow-hover-bg);
  --color-glow-hover-border: var(--glow-hover-border);
  --color-glow-hover-shadow: var(--glow-hover-shadow);
  /* L3 Misc */
  --color-ring-offset: var(--ring-offset);
  --color-disabled: var(--disabled);
  /* L3 Scene gradients */
  --color-alert-urgent-from: var(--alert-urgent-from);
  --color-alert-urgent-to: var(--alert-urgent-to);
  --color-alert-important-from: var(--alert-important-from);
  --color-alert-important-to: var(--alert-important-to);
  --color-alert-warning-from: var(--alert-warning-from);
  --color-alert-warning-to: var(--alert-warning-to);
  --color-overlay-from: var(--overlay-from);
  --color-overlay-to: var(--overlay-to);
  --color-ambient-to: var(--ambient-to);
}

:root {
  /* L2 Semantic - Light mode */
  --heading: oklch(0.21 0.006 285.885);
  --body: oklch(0.37 0.013 285.805);
  --caption: oklch(0.552 0.016 285.938);
  --hint: oklch(0.705 0.015 286.067);
  --placeholder: oklch(0.705 0.015 286.067);
  --inverse: #ffffff;
  --surface: #ffffff;
  --surface-hover: rgba(0, 0, 0, 0.05);
  --surface-faint: rgba(255, 255, 255, 0.2);
  --elevated: oklch(0.985 0 0);
  --inset: oklch(0.967 0.001 286.375);
  --overlay: rgba(0, 0, 0, 0.4);
  --divider: oklch(0.92 0.004 286.32);
  --divider-subtle: oklch(0.967 0.001 286.375);
  --divider-strong: oklch(0.871 0.006 286.286);
  /* L3 Accents - Light mode */
  --accent-sky: oklch(0.685 0.169 237.323);
  --accent-teal: oklch(0.6 0.118 184.704);
  --accent-emerald: oklch(0.696 0.17 162.48);
  --accent-amber: oklch(0.769 0.188 70.08);
  --accent-red: oklch(0.637 0.237 25.331);
  --accent-rose: oklch(0.645 0.246 16.439);
  --accent-orange: oklch(0.705 0.213 47.604);
  --accent-indigo: oklch(0.585 0.233 277.117);
  --accent-yellow: oklch(0.795 0.184 86.047);
  --accent-green: oklch(0.627 0.194 149.214);
  /* L3 Active - Light mode */
  --option-active-bg: rgba(20, 184, 166, 0.1);
  --option-active-border: rgba(20, 184, 166, 0.5);
  --option-active-text: #0d9488;
  --option-active-shadow: 0 0 12px rgba(20, 184, 166, 0.1);
  /* ... more variables */
}

.dark {
  /* L2 Semantic - Dark mode */
  --heading: oklch(0.985 0 0);
  --body: oklch(0.871 0.006 286.286);
  --caption: oklch(0.705 0.015 286.067);
  --hint: oklch(0.552 0.016 285.938);
  --placeholder: oklch(0.442 0.017 285.786);
  --inverse: oklch(0.985 0 0);
  --surface: oklch(0.21 0.006 285.885);
  --surface-hover: rgba(255, 255, 255, 0.05);
  --surface-faint: rgba(0, 0, 0, 0.2);
  --elevated: oklch(0.274 0.006 286.033);
  --inset: oklch(0.141 0.005 285.823);
  --overlay: rgba(0, 0, 0, 0.6);
  --divider: rgba(255, 255, 255, 0.1);
  --divider-subtle: rgba(255, 255, 255, 0.05);
  --divider-strong: rgba(255, 255, 255, 0.2);
  /* L3 Accents - Dark mode */
  --accent-sky: oklch(0.746 0.16 232.661);
  --accent-teal: oklch(0.777 0.152 181.912);
  --accent-emerald: oklch(0.765 0.177 163.223);
  --accent-amber: oklch(0.828 0.189 84.429);
  --accent-red: oklch(0.704 0.191 22.216);
  --accent-rose: oklch(0.712 0.194 13.428);
  --accent-orange: oklch(0.75 0.183 55.934);
  --accent-indigo: oklch(0.673 0.182 276.935);
  --accent-yellow: oklch(0.852 0.199 91.936);
  --accent-green: oklch(0.792 0.209 151.711);
  /* L3 Active - Dark mode */
  --option-active-bg: rgba(20, 184, 166, 0.2);
  --option-active-text: #5eead4;
  --option-active-shadow: 0 0 12px rgba(20, 184, 166, 0.15);
  /* ... more variables */
}
```

## 2. Key Differences from v3

| Aspect | v4 | v3 |
|--------|-----|-----|
| Config file | CSS-based (`index.css`) | JS-based (`tailwind.config.js`) |
| Variable registration | `@theme inline` | `theme.extend.colors` |
| Dark mode | `@custom-variant dark` | `darkMode: 'class'` |
| Class generation | `text-heading` reads `--color-heading` | Same, but via JS config |
| No config file needed | Yes | No |

## 3. Migration Notes

- v4 uses `@import "tailwindcss"` instead of directives
- v4 `@theme inline` registers `--color-*` variables that become Tailwind utility classes
- The `:root` / `.dark` CSS variable assignments are identical to v3
- v4 supports arbitrary values like `bg-[var(--custom)]` but prefers registered variables
- v4's `@layer utilities` works the same for custom classes like `.glass-panel`
