# Tailwind CSS v3 Setup Guide

For Tailwind v3 projects, CSS variables are configured through `tailwind.config.js` (or `.ts`) using `theme.extend`.

## 1. Configuration File

```js
// tailwind.config.js
module.exports = {
  darkMode: 'class', // or 'media'
  theme: {
    extend: {
      colors: {
        // L2 Semantic text colors
        heading: 'var(--color-heading)',
        body: 'var(--color-body)',
        caption: 'var(--color-caption)',
        hint: 'var(--color-hint)',
        placeholder: 'var(--color-placeholder)',
        inverse: 'var(--color-inverse)',
        // L2 Semantic surface colors
        surface: 'var(--color-surface)',
        'surface-hover': 'var(--color-surface-hover)',
        'surface-faint': 'var(--color-surface-faint)',
        elevated: 'var(--color-elevated)',
        inset: 'var(--color-inset)',
        overlay: 'var(--color-overlay)',
        // L2 Semantic border colors
        divider: 'var(--color-divider)',
        'divider-subtle': 'var(--color-divider-subtle)',
        'divider-strong': 'var(--color-divider-strong)',
        // L3 Accent colors
        'accent-sky': 'var(--color-accent-sky)',
        'accent-teal': 'var(--color-accent-teal)',
        'accent-emerald': 'var(--color-accent-emerald)',
        'accent-amber': 'var(--color-accent-amber)',
        'accent-red': 'var(--color-accent-red)',
        'accent-rose': 'var(--color-accent-rose)',
        'accent-orange': 'var(--color-accent-orange)',
        'accent-indigo': 'var(--color-accent-indigo)',
        'accent-yellow': 'var(--color-accent-yellow)',
        'accent-green': 'var(--color-accent-green)',
        // L3 Active/selected state
        'option-active-bg': 'var(--color-option-active-bg)',
        'option-active-border': 'var(--color-option-active-border)',
        'option-active-text': 'var(--color-option-active-text)',
        // L3 Badge text colors
        'badge-sky-text': 'var(--color-badge-sky-text)',
        'badge-amber-text': 'var(--color-badge-amber-text)',
        'badge-red-text': 'var(--color-badge-red-text)',
        'badge-rose-text': 'var(--color-badge-rose-text)',
        // L3 Glass/glow utilities
        'glass-bg': 'var(--color-glass-bg)',
        'glass-border': 'var(--color-glass-border)',
        'glow-hover-bg': 'var(--color-glow-hover-bg)',
        'glow-hover-border': 'var(--color-glow-hover-border)',
        'glow-hover-shadow': 'var(--color-glow-hover-shadow)',
        // L3 Misc
        'ring-offset': 'var(--color-ring-offset)',
        disabled: 'var(--color-disabled)',
      },
      boxShadow: {
        'option-active-shadow': 'var(--color-option-active-shadow)',
      },
    },
  },
};
```

## 2. Global CSS Variables

In your global CSS file (e.g., `src/index.css` or `src/globals.css`):

```css
:root {
  /* L2 Semantic - Light mode */
  --color-heading: #18181b;
  --color-body: #52525b;
  --color-caption: #71717a;
  --color-hint: #a1a1aa;
  --color-placeholder: #a1a1aa;
  --color-inverse: #ffffff;
  --color-surface: #ffffff;
  --color-surface-hover: rgba(0, 0, 0, 0.05);
  --color-surface-faint: rgba(255, 255, 255, 0.2);
  --color-elevated: #fafafa;
  --color-inset: #f4f4f5;
  --color-overlay: rgba(0, 0, 0, 0.4);
  --color-divider: #e4e4e7;
  --color-divider-subtle: #f4f4f5;
  --color-divider-strong: #d4d4d8;
  /* L3 Accents - Light mode */
  --color-accent-sky: #0ea5e9;
  --color-accent-teal: #0d9488;
  --color-accent-emerald: #10b981;
  --color-accent-amber: #f59e0b;
  --color-accent-red: #ef4444;
  --color-accent-rose: #f43f5e;
  --color-accent-orange: #f97316;
  --color-accent-indigo: #6366f1;
  --color-accent-yellow: #eab308;
  --color-accent-green: #16a34a;
  /* ... add more as needed */
}

.dark {
  /* L2 Semantic - Dark mode */
  --color-heading: #fafafa;
  --color-body: #d4d4d8;
  --color-caption: #a1a1aa;
  --color-hint: #71717a;
  --color-placeholder: #52525b;
  --color-inverse: #09090b;
  --color-surface: #18181b;
  --color-surface-hover: rgba(255, 255, 255, 0.05);
  --color-surface-faint: rgba(0, 0, 0, 0.2);
  --color-elevated: #27272a;
  --color-inset: #09090b;
  --color-overlay: rgba(0, 0, 0, 0.6);
  --color-divider: rgba(255, 255, 255, 0.1);
  --color-divider-subtle: rgba(255, 255, 255, 0.05);
  --color-divider-strong: rgba(255, 255, 255, 0.2);
  /* L3 Accents - Dark mode */
  --color-accent-sky: #38bdf8;
  --color-accent-teal: #2dd4bf;
  --color-accent-emerald: #34d399;
  --color-accent-amber: #fbbf24;
  --color-accent-red: #f87171;
  --color-accent-rose: #fb7185;
  --color-accent-orange: #fb923c;
  --color-accent-indigo: #818cf8;
  --color-accent-yellow: #facc15;
  --color-accent-green: #4ade80;
  /* ... mirror all light mode variables */
}
```

## 3. Key Differences from v4

| Aspect | v3 | v4 |
|--------|-----|-----|
| Config file | `tailwind.config.js` | `index.css` (CSS-based) |
| Variable registration | `theme.extend.colors` | `@theme inline` |
| Dark mode | `darkMode: 'class'` | `@custom-variant dark` |
| Arbitrary values | `bg-[var(--x)]` | `bg-x` (if registered) |
| Build tool | PostCSS plugin | Vite/standalone CSS |

## 4. Migration Notes

- v3 requires `darkMode: 'class'` in config for `.dark` class-based switching
- v3 colors registered in `theme.extend.colors` become available as `bg-*`, `text-*`, `border-*`, etc.
- v3 does NOT support `@theme inline` — all variables must go through JS config
- The CSS variable assignment (`:root` / `.dark`) is identical between v3 and v4
