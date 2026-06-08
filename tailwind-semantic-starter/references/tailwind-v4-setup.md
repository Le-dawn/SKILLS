# Tailwind CSS v4 Setup Guide

For Tailwind v4 projects, configuration is CSS-first via `@theme inline` in the global CSS file.

## 1. Install Tailwind v4

```bash
npm install -D tailwindcss@latest
```

For Vite projects:
```bash
npm install -D @tailwindcss/vite
```

Then add the plugin to `vite.config.ts`:
```ts
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [tailwindcss()],
});
```

## 2. Global CSS File

Create `src/index.css` with the following structure:

```css
@import "tailwindcss";

@custom-variant dark (&:is(.dark *));

@theme inline {
  /* Register your semantic variables here */
  --color-heading: var(--heading);
  --color-body: var(--body);
  /* ... more variables ... */
}

:root {
  /* Light mode values */
  --heading: oklch(0.21 0.006 285.885);
  --body: oklch(0.37 0.013 285.805);
  /* ... more variables ... */
}

.dark {
  /* Dark mode values */
  --heading: oklch(0.985 0 0);
  --body: oklch(0.871 0.006 286.286);
  /* ... more variables ... */
}

@layer base {
  body {
    @apply text-heading;
    background-color: var(--body-bg);
  }
}
```

> **Full template**: See `assets/starter-template/src/index.css` for a complete, production-ready configuration.

## 3. Key Points

- `@theme inline` registers `--color-*` variables as Tailwind utility classes
- `:root` and `.dark` assign the actual color values
- No `tailwind.config.js` needed for v4
- Use `@custom-variant dark` to enable `.dark` class-based switching

## 4. Dark Mode Toggle (React Example)

```tsx
// Wrap your app with a theme provider
import { ThemeProvider } from "next-themes"; // or your own implementation

<ThemeProvider attribute="class" defaultTheme="system">
  <App />
</ThemeProvider>
```

Or a minimal toggle:
```tsx
function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
  }, [isDark]);

  return (
    <button onClick={() => setIsDark(!isDark)}>
      {isDark ? "🌙" : "☀️"}
    </button>
  );
}
```
