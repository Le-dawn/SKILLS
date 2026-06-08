/**
 * App.tsx — Semantic Starter Example
 *
 * Demonstrates how to use semantic variables instead of
 * hardcoded colors or `dark:` prefixes.
 *
 * Rules demonstrated:
 * 1. text-heading / text-body / text-caption for text hierarchy
 * 2. bg-surface / bg-elevated / bg-inset for surface hierarchy
 * 3. border-divider for borders
 * 4. text-accent-* / bg-accent-* for emphasis
 * 5. glass-panel / glow-hover utility classes
 * 6. NO `dark:` prefixes anywhere
 */

import { ExampleCard } from "./components/ExampleCard";

function App() {
  return (
    <div className="min-h-screen p-6 md:p-10">
      {/* Page title */}
      <h1 className="text-3xl font-bold text-heading mb-2">
        Semantic Starter
      </h1>
      <p className="text-body mb-8">
        This page uses only semantic variables — no dark: prefixes needed.
      </p>

      {/* Card grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ExampleCard
          title="Surface Hierarchy"
          description="bg-surface, bg-elevated, bg-inset adapt automatically to light/dark mode."
          accent="teal"
        />
        <ExampleCard
          title="Text Hierarchy"
          description="text-heading, text-body, text-caption, text-hint create readable contrast in both modes."
          accent="sky"
        />
        <ExampleCard
          title="Glass Panel"
          description="The glass-panel utility works in both modes with a single class."
          accent="indigo"
        />
      </div>

      {/* Accent color showcase */}
      <section className="mt-10">
        <h2 className="text-xl font-semibold text-heading mb-4">
          Accent Colors
        </h2>
        <div className="flex flex-wrap gap-3">
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-sky-500/10 text-accent-sky border border-sky-500/20">sky</span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-teal-500/10 text-accent-teal border border-teal-500/20">teal</span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-emerald-500/10 text-accent-emerald border border-emerald-500/20">emerald</span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-amber-500/10 text-accent-amber border border-amber-500/20">amber</span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-500/10 text-accent-red border border-red-500/20">red</span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-rose-500/10 text-accent-rose border border-rose-500/20">rose</span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-orange-500/10 text-accent-orange border border-orange-500/20">orange</span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-indigo-500/10 text-accent-indigo border border-indigo-500/20">indigo</span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-yellow-500/10 text-accent-yellow border border-yellow-500/20">yellow</span>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-500/10 text-accent-green border border-green-500/20">green</span>
        </div>
        <p className="text-caption mt-3 text-sm">
          Each accent uses explicit Tailwind classes like{" "}
          <code className="text-accent-sky">text-accent-sky</code>{" "}
          paired with a tint like <code className="text-accent-sky">bg-sky-500/10</code>.
        </p>
      </section>
    </div>
  );
}

export default App;
