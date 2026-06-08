/**
 * ExampleCard.tsx — Component Pattern Demo
 *
 * A reusable card component demonstrating the semantic variable system.
 * No `dark:` prefixes. No hardcoded zinc/gray colors.
 */

interface ExampleCardProps {
  title: string;
  description: string;
  accent: "sky" | "teal" | "emerald" | "amber" | "red" | "rose" | "orange" | "indigo" | "yellow" | "green";
}

const accentMap: Record<string, string> = {
  sky: "text-accent-sky border-accent-sky/20 bg-sky-500/10",
  teal: "text-accent-teal border-accent-teal/20 bg-teal-500/10",
  emerald: "text-accent-emerald border-accent-emerald/20 bg-emerald-500/10",
  amber: "text-accent-amber border-accent-amber/20 bg-amber-500/10",
  red: "text-accent-red border-accent-red/20 bg-red-500/10",
  rose: "text-accent-rose border-accent-rose/20 bg-rose-500/10",
  orange: "text-accent-orange border-accent-orange/20 bg-orange-500/10",
  indigo: "text-accent-indigo border-accent-indigo/20 bg-indigo-500/10",
  yellow: "text-accent-yellow border-accent-yellow/20 bg-yellow-500/10",
  green: "text-accent-green border-accent-green/20 bg-green-500/10",
};

export function ExampleCard({ title, description, accent }: ExampleCardProps) {
  const accentClasses = accentMap[accent] || accentMap.sky;

  return (
    <div className="glass-panel rounded-xl p-5 glow-hover">
      {/* Accent badge */}
      <span
        className={`inline-block px-2 py-0.5 rounded text-xs font-medium border ${accentClasses}`}
      >
        {accent}
      </span>

      {/* Title */}
      <h3 className="text-lg font-semibold text-heading mt-3">{title}</h3>

      {/* Description */}
      <p className="text-body mt-1 text-sm leading-relaxed">{description}</p>

      {/* Footer hint */}
      <div className="mt-4 pt-3 border-t border-divider-subtle">
        <p className="text-caption text-xs">
          Hover this card to see the glow-hover effect.
        </p>
      </div>
    </div>
  );
}
