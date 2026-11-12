---
name: batter-h3-prompt-writing
description: Plan long videos as coherent generation segments and write standalone MiniMax H3 prompts for T2VA, I2VA, FL2VA, L2VA, and Ref2VA. Use for multi-prompt duration allocation, narrative beats, cross-segment continuity, reference mapping, or single-prompt rewriting.
compatibility: Portable to any agent that can read local files — no external API calls, MiniMax Hub tools, or proprietary runtime required. The agents/openai.yaml file only adds optional ChatGPT/Codex UI metadata; it does not restrict the skill to OpenAI agents.
---

# Batter H3 Prompt Writing

## Workflow

1. Determine whether the request concerns one generation or a sequence of generations. For long videos, multiple prompts, continuation chains, or segment-boundary review, first read `references/long-video-planning.md` and plan the segments before drafting their prompts. For a single prompt, proceed directly.
2. Identify the input mode for each segment: T2VA, I2VA, FL2VA, L2VA, or full-reference Ref2VA.
3. For base text/keyframe modes, read `references/base-en.txt` and follow its final prompt structure.
4. For full-reference mode, read `references/ref-en.txt` and follow its six-section rewrite format.
5. Preserve the exact field names, section order, labels, and timing notation from the selected guide.

## Long-Video Planning

A generation segment is one model request; a shot is one continuous camera view within that segment. Plan both levels explicitly. Do not assume one prompt equals one shot or split the story mechanically into maximum-length segments.

Use `references/long-video-planning.md` for beat-based splitting, dialogue and action budgets, global/local timing, continuity handoffs, reference manifests, prompt packaging, and review. Keep planning metadata outside the H3 payload; the selected base or full-reference guide still defines its exact fields. Planning notes may use the user’s language; final H3 rewrite sections follow the English rules below.

This skill produces plans and prompts. It does not require generation, uploading assets, or running a production pipeline. If the user asks only for planning or review, deliver that scope without generating every prompt.

## Base Modes

- T2VA: build the full audiovisual timeline from text.
- I2VA: start from the first frame and develop forward from it.
- FL2VA: describe the continuous path between the first and last frames.
- L2VA: infer a plausible opening and converge to the supplied last frame.

Use `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music` in the order shown in `references/base-en.txt`.

## Full-Reference Mode

Ref2VA rewrites use `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, and `non_diegetic_music` in that order. Reference labels stay consistent across all sections.

Read `references/ref-en.txt` for label rules, retention analysis, and complete examples.

## Output Rules

- Write rewrite sections in English; preserve dialogue, lyrics, and visible scene text in their original language.
- Describe each shot by composition, subjects, environment, actions, camera, sound, and the exact point where referenced content appears.
- Avoid plot summaries, unresolved reference labels, and timing that does not match the requested duration.
## Tips for Better Results
- Always match the total duration of the description to the requested generation duration (the inherited default is 4–15 seconds per segment, not a limit on the assembled film). Use explicit limits from the chosen workflow when supplied; do not assume every mode supports the same durations. For a long video, reconcile the assembled duration separately using the planning guide.
- Keep reference labels consistent (e.g. `<Picture 1>`, `<Video 1>`, `<Audio 1>`) across every section.
- Prefer concrete visual and audio details over abstract words like "cinematic" or "beautiful".
- When using keyframes (I2VA / FL2VA / L2VA), clearly state how the first and/or last frame connects to the timeline.
