/**
 * tailwind.config.js — v3 Backup Configuration
 *
 * If your project uses Tailwind v3 instead of v4,
 * use this config file together with the CSS variables
 * defined in src/index.css (the :root and .dark blocks).
 *
 * For v4 projects, this file is NOT needed — everything
 * is configured in CSS via @theme inline.
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // L1 shadcn/ui Base (optional — only if using shadcn)
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: "var(--primary)",
        "primary-foreground": "var(--primary-foreground)",
        secondary: "var(--secondary)",
        "secondary-foreground": "var(--secondary-foreground)",
        muted: "var(--muted)",
        "muted-foreground": "var(--muted-foreground)",
        accent: "var(--accent)",
        "accent-foreground": "var(--accent-foreground)",
        destructive: "var(--destructive)",
        "destructive-foreground": "var(--destructive-foreground)",
        border: "var(--border)",
        input: "var(--input)",
        ring: "var(--ring)",

        // L2 Semantic Text
        heading: "var(--heading)",
        body: "var(--body)",
        caption: "var(--caption)",
        hint: "var(--hint)",
        placeholder: "var(--placeholder)",
        inverse: "var(--inverse)",

        // L2 Semantic Surface
        surface: "var(--surface)",
        "surface-hover": "var(--surface-hover)",
        "surface-faint": "var(--surface-faint)",
        elevated: "var(--elevated)",
        inset: "var(--inset)",
        overlay: "var(--overlay)",

        // L2 Semantic Border
        divider: "var(--divider)",
        "divider-subtle": "var(--divider-subtle)",
        "divider-strong": "var(--divider-strong)",

        // L3 Accents
        "accent-sky": "var(--accent-sky)",
        "accent-teal": "var(--accent-teal)",
        "accent-emerald": "var(--accent-emerald)",
        "accent-amber": "var(--accent-amber)",
        "accent-red": "var(--accent-red)",
        "accent-rose": "var(--accent-rose)",
        "accent-orange": "var(--accent-orange)",
        "accent-indigo": "var(--accent-indigo)",
        "accent-yellow": "var(--accent-yellow)",
        "accent-green": "var(--accent-green)",

        // L3 Active
        "option-active-bg": "var(--option-active-bg)",
        "option-active-border": "var(--option-active-border)",
        "option-active-text": "var(--option-active-text)",

        // L3 Badge
        "badge-sky-text": "var(--badge-sky-text)",
        "badge-amber-text": "var(--badge-amber-text)",
        "badge-red-text": "var(--badge-red-text)",
        "badge-rose-text": "var(--badge-rose-text)",

        // L3 Glass / Glow
        "glass-bg": "var(--glass-bg)",
        "glass-border": "var(--glass-border)",
        "glow-hover-bg": "var(--glow-hover-bg)",
        "glow-hover-border": "var(--glow-hover-border)",

        // L3 Misc
        "ring-offset": "var(--ring-offset)",
        disabled: "var(--disabled)",
      },
      boxShadow: {
        "option-active-shadow": "var(--option-active-shadow)",
        "glow-hover-shadow": "var(--glow-hover-shadow)",
      },
    },
  },
  plugins: [],
};
