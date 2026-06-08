# Tailwind CSS v3 Setup Guide

For Tailwind v3 projects, CSS variables are configured through `tailwind.config.js` using `theme.extend`.

## 1. Install Tailwind v3

```bash
npm install -D tailwindcss@3 postcss autoprefixer
npx tailwindcss init -p
```

## 2. Configuration File

Update `tailwind.config.js`:

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        heading: "var(--heading)",
        body: "var(--body)",
        caption: "var(--caption)",
        hint: "var(--hint)",
        placeholder: "var(--placeholder)",
        inverse: "var(--inverse)",
        surface: "var(--surface)",
        "surface-hover": "var(--surface-hover)",
        elevated: "var(--elevated)",
        inset: "var(--inset)",
        overlay: "var(--overlay)",
        divider: "var(--divider)",
        "divider-subtle": "var(--divider-subtle)",
        "divider-strong": "var(--divider-strong)",
        "accent-sky": "var(--accent-sky)",
        "accent-teal": "var(--accent-teal)",
        /* ... add more as needed ... */
      },
    },
  },
  plugins: [],
};
```

## 3. Global CSS Variables

In your global CSS file (e.g., `src/index.css`):

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --heading: #18181b;
  --body: #52525b;
  --caption: #71717a;
  /* ... light mode values ... */
}

.dark {
  --heading: #fafafa;
  --body: #d4d4d8;
  --caption: #a1a1aa;
  /* ... dark mode values ... */
}

@layer base {
  body {
    @apply bg-surface text-heading;
  }
}
```

> **Full template**: See `assets/starter-template/tailwind.config.js` for a complete v3 configuration.

## 4. Key Points

- `darkMode: "class"` enables `.dark` class-based switching
- All variables registered in `theme.extend.colors` become utility classes
- The CSS variable assignments in `:root` / `.dark` are identical to v4
- v3 does NOT support `@theme inline` — use JS config instead
