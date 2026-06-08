# Component Patterns Library

Ready-to-use component templates using semantic variables only.

> **Prohibitions**
> - No `dark:` prefixes
> - No hardcoded `text-zinc-*` / `bg-zinc-*` / `border-zinc-*`
> - No `bg-white` / `bg-black` / `text-white` / `text-black`

---

## 1. Panel / Card Container

```tsx
<div className="rounded-xl border border-divider bg-surface p-5 shadow-sm">
  <h3 className="text-lg font-semibold text-heading">Card Title</h3>
  <p className="text-body mt-1">Card description text.</p>
</div>
```

**Variants**:
- Elevated card: `bg-elevated` instead of `bg-surface`
- Glass card: add `glass-panel` utility class
- Inset panel: `bg-inset border-divider-subtle`

---

## 2. Button

### Primary Button
```tsx
<button className="px-4 py-2 rounded-lg bg-accent-sky text-inverse font-medium
  hover:opacity-90 active:scale-[0.98] transition-all duration-200">
  Primary Action
</button>
```

### Secondary Button
```tsx
<button className="px-4 py-2 rounded-lg bg-surface border border-divider text-heading
  hover:bg-surface-hover active:scale-[0.98] transition-all duration-200">
  Secondary Action
</button>
```

### Ghost Button
```tsx
<button className="px-4 py-2 rounded-lg text-heading
  hover:bg-surface-hover active:scale-[0.98] transition-all duration-200">
  Ghost Action
</button>
```

### Icon Button
```tsx
<button className="p-2 rounded-lg text-caption hover:text-heading hover:bg-surface-hover
  transition-all duration-200">
  <Icon className="w-5 h-5" />
</button>
```

---

## 3. Input Field

```tsx
<div className="space-y-1.5">
  <label className="text-sm font-medium text-heading">Label</label>
  <input
    className="w-full px-3 py-2 rounded-lg bg-inset border border-divider
      text-heading placeholder:text-placeholder
      focus:outline-none focus:ring-2 focus:ring-accent-sky/50 focus:border-accent-sky
      transition-all duration-200"
    placeholder="Enter value..."
  />
  <p className="text-xs text-caption">Helper text goes here.</p>
</div>
```

---

## 4. Select / Dropdown

```tsx
<select className="w-full px-3 py-2 rounded-lg bg-inset border border-divider
  text-heading focus:outline-none focus:ring-2 focus:ring-accent-sky/50
  transition-all duration-200 appearance-none">
  <option value="">Select an option</option>
  <option value="1">Option 1</option>
  <option value="2">Option 2</option>
</select>
```

> Note: `option` elements are styled globally in `@layer base` using `--surface` and `--heading` variables.

---

## 5. List Item

```tsx
<div className="flex items-center gap-3 px-4 py-3 rounded-lg
  hover:bg-surface-hover transition-all duration-200 cursor-pointer">
  <div className="w-8 h-8 rounded-full bg-accent-sky/10 flex items-center justify-center">
    <Icon className="w-4 h-4 text-accent-sky" />
  </div>
  <div className="flex-1 min-w-0">
    <p className="text-sm font-medium text-heading truncate">Item Title</p>
    <p className="text-xs text-caption truncate">Item description</p>
  </div>
  <span className="text-xs text-hint">Time</span>
</div>
```

---

## 6. Status Badge / Tag

### Basic Badge
```tsx
<span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
  bg-accent-sky/10 text-accent-sky border border-accent-sky/20">
  Active
</span>
```

### Level Badge (using badge-*-text variables)
```tsx
<span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
  bg-accent-amber/10 text-badge-amber-text">
  Warning
</span>
```

### Tag / Pill (PromptPanel style)
```tsx
<span className="inline-flex items-center px-3 py-1 rounded-lg text-sm
  bg-tag-active-bg border border-tag-active-border text-tag-active-text
  hover:bg-tag-active-hover-bg transition-all duration-200 cursor-pointer">
  Tag Label
</span>
```

---

## 7. Alert / Notification Card

```tsx
<div className="rounded-xl border border-accent-amber/30 p-4
  bg-gradient-to-r from-alert-important-from to-alert-important-to">
  <div className="flex items-start gap-3">
    <AlertIcon className="w-5 h-5 text-accent-amber mt-0.5 shrink-0" />
    <div>
      <h4 className="text-sm font-semibold text-heading">Important Notice</h4>
      <p className="text-sm text-body mt-1">Alert description goes here.</p>
    </div>
  </div>
</div>
```

**Severity variants**:
- Info: `from-alert-warning-from to-alert-warning-to` + `text-accent-sky`
- Warning: `from-alert-important-from to-alert-important-to` + `text-accent-amber`
- Error: `from-alert-urgent-from to-alert-urgent-to` + `text-accent-red`

---

## 8. Modal / Dialog Overlay

```tsx
{/* Backdrop */}
<div className="fixed inset-0 bg-overlay z-40" />

{/* Modal */}
<div className="fixed inset-0 z-50 flex items-center justify-center p-4">
  <div className="w-full max-w-md rounded-2xl border border-divider bg-surface shadow-xl p-6">
    <h2 className="text-xl font-semibold text-heading">Modal Title</h2>
    <p className="text-body mt-2">Modal content goes here.</p>
    <div className="flex justify-end gap-3 mt-6">
      <button className="px-4 py-2 rounded-lg text-caption hover:text-heading
        hover:bg-surface-hover transition-all duration-200">
        Cancel
      </button>
      <button className="px-4 py-2 rounded-lg bg-accent-sky text-inverse font-medium
        hover:opacity-90 transition-all duration-200">
        Confirm
      </button>
    </div>
  </div>
</div>
```

---

## 9. Sidebar / Navigation

```tsx
<nav className="w-64 h-screen border-r border-divider bg-surface flex flex-col">
  <div className="p-4 border-b border-divider">
    <h1 className="text-lg font-bold text-heading">App Name</h1>
  </div>
  <div className="flex-1 py-2 space-y-0.5">
    {items.map((item) => (
      <a
        key={item.id}
        href={item.href}
        className={`flex items-center gap-3 px-4 py-2 mx-2 rounded-lg text-sm
          transition-all duration-200
          ${item.active
            ? "bg-option-active-bg border border-option-active-border text-option-active-text"
            : "text-body hover:bg-surface-hover hover:text-heading"
          }`}
      >
        <item.icon className="w-5 h-5" />
        {item.label}
      </a>
    ))}
  </div>
</nav>
```

---

## 10. Table

```tsx
<table className="w-full text-sm">
  <thead>
    <tr className="border-b border-divider">
      <th className="text-left py-3 px-4 font-medium text-caption">Column</th>
      <th className="text-left py-3 px-4 font-medium text-caption">Column</th>
    </tr>
  </thead>
  <tbody>
    <tr className="border-b border-divider-subtle hover:bg-surface-hover transition-colors">
      <td className="py-3 px-4 text-heading">Cell value</td>
      <td className="py-3 px-4 text-body">Cell value</td>
    </tr>
  </tbody>
</table>
```

---

## 11. Toggle / Switch

```tsx
<button
  onClick={toggle}
  className={`relative inline-flex h-6 w-11 items-center rounded-full
    transition-colors duration-200
    ${enabled ? "bg-accent-sky" : "bg-divider-strong"}`}
>
  <span
    className={`inline-block h-4 w-4 transform rounded-full bg-inverse
      transition-transform duration-200
      ${enabled ? "translate-x-6" : "translate-x-1"}`}
  />
</button>
```

---

## 12. Skeleton / Loading

```tsx
<div className="animate-pulse space-y-3">
  <div className="h-4 bg-divider-subtle rounded w-3/4" />
  <div className="h-4 bg-divider-subtle rounded w-1/2" />
  <div className="h-20 bg-divider-subtle rounded" />
</div>
```

---

## Spacing & Sizing Conventions

| Element | Padding | Gap | Border Radius |
|---------|---------|-----|---------------|
| Card / Panel | `p-5` (20px) | — | `rounded-xl` |
| List item | `py-3 px-4` | `gap-3` | `rounded-lg` |
| Button | `px-4 py-2` | — | `rounded-lg` |
| Input | `px-3 py-2` | — | `rounded-lg` |
| Badge / Tag | `px-2 py-0.5` | — | `rounded-full` or `rounded-lg` |
| Icon container | `p-2` | — | `rounded-lg` or `rounded-full` |
| Modal | `p-6` | — | `rounded-2xl` |

---

## Motion Conventions

```
transition-all duration-200    — Default hover/active transitions
transition-colors duration-150 — Color-only transitions
transform active:scale-[0.98]  — Button press feedback
transform hover:scale-105      — Card hover lift (subtle)
```
