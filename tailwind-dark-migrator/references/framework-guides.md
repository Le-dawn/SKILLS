# Framework-Specific Scanning Guides

This reference describes how `dark:` patterns appear in different frontend frameworks and what to watch for during scanning and replacement.

## React / JSX / TSX

### ClassName Format

```tsx
// Standard className string
<div className="text-zinc-900 dark:text-zinc-100">

// Conditional with template literal
<div className={`px-4 ${isActive ? 'bg-teal-500/10 dark:bg-teal-500/20' : 'bg-elevated'}`}>

// With cn() utility
<div className={cn("text-body", isActive && "bg-option-active-bg text-option-active-text")}>

// Multiple lines (common in complex components)
className={`
  flex items-center gap-2
  text-zinc-700 dark:text-zinc-300
  hover:bg-black/5 dark:hover:bg-white/5
`}
```

### Scanning Notes
- `dark:` patterns can span across line breaks in template literals
- Watch for `cn()` calls that concatenate conditional classes
- JSX comments `{/* ... */}` may contain disabled code with dark: patterns

## Vue / Single File Components

### Class Binding Formats

```vue
<!-- Standard class -->
<div class="text-zinc-900 dark:text-zinc-100">

<!-- Dynamic class binding -->
<div :class="{ 'bg-teal-500/10 dark:bg-teal-500/20': isActive, 'bg-elevated': !isActive }">

<!-- Array syntax -->
<div :class="['text-body', isActive ? 'text-accent-teal' : 'text-caption']">

<!-- Template literal in script -->
const classes = computed(() => `
  flex items-center
  ${isActive ? 'bg-option-active-bg' : 'bg-elevated'}
`)
```

### Scanning Notes
- Vue uses `:class` instead of `className`
- Class objects (`:class="{ ... }"`) require parsing keys
- Vue files contain `<template>`, `<script>`, and `<style>` sections — only scan template and script
- `<style scoped>` may contain `.dark` selectors that need migration too

## Svelte

### Class Directives

```svelte
<!-- Standard class -->
<div class="text-zinc-900 dark:text-zinc-100">

<!-- Class directive (shorthand) -->
<div class:bg-option-active-bg={isActive} class:text-option-active-text={isActive}>

<!-- Conditional class -->
<div class={isActive ? 'bg-teal-500/10 dark:bg-teal-500/20' : 'bg-elevated'}>
```

### Scanning Notes
- Svelte's `class:` directives compile to conditional classes
- `{#if}` blocks may wrap elements with dark: patterns
- Svelte `<style>` blocks can contain global `.dark` selectors

## HTML / Plain CSS

### Format

```html
<div class="text-zinc-900 dark:text-zinc-100">
```

### Scanning Notes
- Simplest case — standard class attribute strings
- May contain Alpine.js or Petite Vue directives: `x-bind:class="..."`

## CSS / SCSS / Less Files

### Dark Mode Patterns

```css
/* Standard Tailwind utility in CSS */
.my-component {
  @apply text-zinc-900 dark:text-zinc-100;
}

/* Manual dark mode media query (legacy) */
@media (prefers-color-scheme: dark) {
  .my-component { color: #fafafa; }
}

/* Class-based dark mode */
.dark .my-component {
  color: #fafafa;
}
```

### Migration Strategy
- `@apply` with `dark:` should be converted to use CSS custom properties
- Manual `.dark` selectors in CSS should use variables: `.my-component { color: var(--heading); }`
- Media query `(prefers-color-scheme: dark)` should be removed in favor of class-based dark mode

## Universal Scanning Rules

Regardless of framework, the scan script `scripts/scan_dark_patterns.py` handles:

1. **Multi-line patterns**: Regex with `re.DOTALL` flag for patterns spanning lines
2. **String delimiters**: Single quotes, double quotes, backticks (template literals)
3. **Escaped characters**: Properly handles `\"` and `\'` within strings
4. **Comments**: Skips or flags commented-out dark: code

### Files to Scan

```
.tsx, .jsx, .vue, .svelte, .html, .css, .scss, .less
```

### Files to Skip

```
node_modules/, .next/, dist/, build/, .git/, coverage/
```
