#!/usr/bin/env python3
"""
Scan a project for all Tailwind `dark:` patterns and classify them.

Usage:
    python scan_dark_patterns.py <project_root> [--output report.json]

Outputs a JSON report with categorized dark: patterns, file locations,
and suggested semantic variable names.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# File extensions to scan
EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte", ".html", ".css", ".scss", ".less"}

# Pattern categories with regex matchers
# Each matcher returns (category_name, suggested_variable) or None
PATTERN_MATCHERS = [
    # L2 Text hierarchy
    (r"text-zinc-900\s+dark:text-zinc-100", "text_color", "text-heading"),
    (r"text-zinc-700\s+dark:text-zinc-300", "text_color", "text-body"),
    (r"text-zinc-600\s+dark:text-zinc-400", "text_color", "text-caption"),
    (r"text-zinc-500\s+dark:text-zinc-400", "text_color", "text-caption"),
    (r"text-zinc-400\s+dark:text-zinc-600", "text_color", "text-placeholder"),
    (r"text-zinc-400\s+dark:text-zinc-500", "text_color", "text-hint"),
    # L2 Surface hierarchy
    (r"bg-white\s+dark:bg-zinc-900", "bg_color", "bg-surface"),
    (r"bg-black/5\s+dark:bg-white/5", "bg_color", "bg-surface-hover"),
    (r"bg-white/60\s+dark:bg-slate-900/40", "bg_color", "bg-glass-bg"),
    # L2 Border hierarchy
    (r"border-black/10\s+dark:border-white/10", "border_color", "border-divider"),
    (r"border-white/10\s+dark:border-white/20", "border_color", "border-divider / border-divider-strong"),
    # L3 Accent colors (text)
    (r"text-sky-500\s+dark:text-sky-400", "accent_color", "text-accent-sky"),
    (r"text-teal-500\s+dark:text-teal-400", "accent_color", "text-accent-teal"),
    (r"text-teal-600\s+dark:text-teal-400", "accent_color", "text-accent-teal"),
    (r"text-emerald-500\s+dark:text-emerald-400", "accent_color", "text-accent-emerald"),
    (r"text-amber-500\s+dark:text-amber-400", "accent_color", "text-accent-amber"),
    (r"text-red-500\s+dark:text-red-400", "accent_color", "text-accent-red"),
    (r"text-rose-500\s+dark:text-rose-400", "accent_color", "text-accent-rose"),
    (r"text-orange-500\s+dark:text-orange-400", "accent_color", "text-accent-orange"),
    (r"text-indigo-500\s+dark:text-indigo-400", "accent_color", "text-accent-indigo"),
    (r"text-yellow-500\s+dark:text-yellow-400", "accent_color", "text-accent-yellow"),
    (r"text-green-500\s+dark:text-green-400", "accent_color", "text-accent-green"),
    (r"text-green-600\s+dark:text-green-400", "accent_color", "text-accent-green"),
    # L3 Accent hover colors
    (r"hover:text-sky-500\s+dark:hover:text-sky-400", "accent_color", "hover:text-accent-sky"),
    (r"hover:text-teal-600\s+dark:hover:text-teal-300", "accent_color", "hover:text-accent-teal"),
    (r"hover:text-red-600\s+dark:hover:text-red-300", "accent_color", "hover:text-accent-red"),
    # L3 Ring colors
    (r"ring-sky-500\s+dark:ring-sky-400", "accent_color", "ring-accent-sky"),
    # Focus ring offset
    (r"ring-offset-white\s+dark:ring-offset-zinc-900", "focus_ring", "ring-offset-ring-offset"),
    (r"ring-offset-white\s+dark:ring-offset-zinc-950", "focus_ring", "ring-offset-ring-offset"),
    # Disabled state
    (r"text-zinc-300\s+dark:text-zinc-700", "disabled", "text-disabled"),
    # Gradients (alert cards)
    (r"from-red-50\s+to-white\s+dark:from-red-950/10\s+dark:to-slate-900", "gradient", "from-alert-urgent-from to-alert-urgent-to"),
    (r"from-amber-50\s+to-white\s+dark:from-amber-950/10\s+dark:to-slate-900", "gradient", "from-alert-important-from to-alert-important-to"),
    (r"from-sky-50\s+to-white\s+dark:from-sky-950/10\s+dark:to-slate-900", "gradient", "from-alert-warning-from to-alert-warning-to"),
    # Overlay gradients
    (r"from-zinc-200/80\s+to-zinc-100/80\s+dark:from-zinc-900/80\s+dark:to-zinc-950/80", "gradient", "from-overlay-from to-overlay-to"),
    # Utility classes
    (r"bg-white/60\s+dark:bg-slate-900/40\s+backdrop-blur", "utility_class", "bg-glass-bg (glass-panel)"),
    (r"hover:shadow-\[.*?\]\s+dark:hover:shadow-\[.*?\]", "utility_class", "shadow-glow-hover-shadow (glow-hover)"),
    (r"hover:border-cyan-500/30\s+dark:hover:border-cyan-500/50", "utility_class", "border-glow-hover-border (glow-hover)"),
    (r"hover:bg-slate-100/60\s+dark:hover:bg-slate-800/60", "utility_class", "bg-glow-hover-bg (glow-hover)"),
]

# Fallback: if no specific matcher, categorize by prefix
def categorize_fallback(line: str) -> tuple:
    """Categorize a dark: pattern when no specific matcher hits."""
    if ("gradient" in line) or (("from-" in line) and ("to-" in line)):
        return "gradient", "TODO: create scene gradient variables"
    if "shadow-" in line and "dark:shadow-" in line:
        return "utility_class", "TODO: create shadow variable"
    if "text-" in line and "dark:text-" in line:
        return "accent_color", "TODO: map to accent-* variable"
    if "bg-" in line and "dark:bg-" in line:
        return "bg_color", "TODO: map to surface/elevated variable"
    if "border-" in line and "dark:border-" in line:
        return "border_color", "TODO: map to divider variable"
    return "other", "TODO: manual review"


def find_dark_patterns(content: str, file_path: str):
    """Find all dark: patterns in a file's content.
    
    Handles both single-line and multi-line (template literal) patterns.
    """
    patterns = []
    lines = content.split("\n")
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if "dark:" not in line:
            i += 1
            continue
        
        # Check for multi-line template literals (backtick strings)
        collected = line
        line_start = i + 1
        if "`" in line and line.count("`") % 2 != 0:
            j = i + 1
            while j < len(lines) and "`" not in lines[j]:
                collected += " " + lines[j].strip()
                j += 1
            if j < len(lines):
                collected += " " + lines[j].strip()
            i = j + 1
        else:
            i += 1
        
        matched = False
        for regex, category, suggestion in PATTERN_MATCHERS:
            if re.search(regex, collected):
                patterns.append({
                    "line": line_start,
                    "content": collected.strip()[:200],
                    "category": category,
                    "suggested_variable": suggestion,
                    "matched": True,
                })
                matched = True
                break

        if not matched:
            cat, sug = categorize_fallback(collected)
            patterns.append({
                "line": line_start,
                "content": collected.strip()[:200],
                "category": cat,
                "suggested_variable": sug,
                "matched": False,
            })

    return patterns


def scan_project(project_root: str):
    """Scan the entire project for dark: patterns."""
    root = Path(project_root)
    results = []
    category_counts = defaultdict(int)
    total_occurrences = 0

    for ext in EXTENSIONS:
        for file_path in root.rglob(f"*{ext}"):
            # Skip node_modules and build dirs
            if "node_modules" in str(file_path) or ".next" in str(file_path) or "dist" in str(file_path):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            patterns = find_dark_patterns(content, str(file_path))
            if not patterns:
                continue

            for p in patterns:
                category_counts[p["category"]] += 1
                total_occurrences += 1

            results.append({
                "path": str(file_path.relative_to(root)),
                "occurrences": len(patterns),
                "patterns": patterns,
            })

    # Sort by occurrence count descending
    results.sort(key=lambda x: x["occurrences"], reverse=True)

    return {
        "summary": {
            "total_files": len(results),
            "total_dark_occurrences": total_occurrences,
            "categories": dict(category_counts),
        },
        "files": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Scan project for Tailwind dark: patterns")
    parser.add_argument("project_root", help="Path to project root directory")
    parser.add_argument("--output", "-o", default="dark-patterns-report.json", help="Output JSON file path")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    if not os.path.isdir(project_root):
        print(f"Error: {project_root} is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {project_root} for dark: patterns...")
    report = scan_project(project_root)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Report written to {args.output}")
    print(f"  Files with dark: : {report['summary']['total_files']}")
    print(f"  Total occurrences: {report['summary']['total_dark_occurrences']}")
    print("\nBreakdown by category:")
    for cat, count in sorted(report["summary"]["categories"].items(), key=lambda x: -x[1]):
        print(f"  {cat:20s}: {count:4d}")


if __name__ == "__main__":
    main()
