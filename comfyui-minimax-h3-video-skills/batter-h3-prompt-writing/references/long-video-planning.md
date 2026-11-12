# Long-Video Segment and Prompt Planning

## Contents

1. Scope and timing
2. Narrative beats and generation boundaries
3. Continuity and references
4. Standalone prompt packaging
5. Delivery and review
6. Worked planning example

## 1. Scope and timing

Use this guide when a film needs multiple generation requests, even if the total film is short. A **segment** is one generation request and one prompt payload. A **shot** is an uninterrupted camera view; one segment can contain several shots, and a continuous-looking shot may require several segments. Never equate a model request boundary with a cinematic cut automatically.

Extract the intended final runtime, story/script, required dialogue, visual style, delivery scope, supplied references, and known workflow duration limits. Reuse existing project decisions. Ask only for missing facts that materially block planning; otherwise state working assumptions and proceed. Do not invent a script, shorten required dialogue, or change the ending merely to fit a duration. If constraints conflict, explain the conflict and provide concrete alternatives.

The inherited skill uses 4–15 seconds as its default generation range, not as a verified universal backend capability. Explicit workflow constraints take precedence. Where supported durations or reference modes are unknown, mark them as assumptions rather than claiming a plan is submission-ready.

Maintain two clocks:

- **Film time:** the segment's intended position in the assembled edit.
- **Generation-local time:** starts at zero for each model request. Restart `[Shot 1]` in each payload, without a timestamp; later shots use local cut times in the base/full-reference format.

Record generated duration G and selected source interval [in, out) for every segment. Kept duration K = out - in, with 0 <= in < out <= G. For ordinary cuts, final duration = sum(K). For overlapping transitions, subtract each overlap once; record separately any added holds or editorial material. Hard cuts do not subtract time. Do not count discarded handles or repeated handoff frames twice. All shots and dialogue must fit G, while essential story content must survive the selected interval.

Plan handles only when useful for a specific edit; do not pad every clip by a fixed amount. Include handles in G and keep G within the workflow limits. If exact runtime is required, reconcile the final edit mathematically. Do not solve an overrun by silently speeding speech or truncating the last segment.

## 2. Narrative beats and generation boundaries

First outline the meaningful changes in knowledge, intention, action, or emotion across the film. For each beat, identify its starting condition, visible or audible event, resulting state, and why the next beat follows. Allocate time to these events before deciding how many prompts to write.

A useful segment usually has one dominant dramatic task and a readable progression: entry state → action or exchange → result/reaction → exit state. This is a planning heuristic, not a mandatory miniature story arc: a deliberate sustained observation or ongoing action may remain unresolved at the boundary.

Prefer boundaries at completed actions, completed lines, held reactions, motivated viewpoint changes, or explicit changes of place/time. Split when the action/dialogue load exceeds the available duration, a reference or mode must change, or a scene transition merits a separate generation. Combine adjacent beats when splitting would break a causal action and they fit naturally together. Do not split solely because a maximum-duration grid reaches its next tick.

Budget the actual performance:

- Use timed readings or supplied audio for dialogue when available. Otherwise estimate conservatively for the language, delivery, pauses, and turn-taking, and mark the estimate. Leave visible reaction and breathing time; do not apply a universal words-per-second rate.
- Give physical actions enough ordered phases to be understandable: reach, grasp, manipulate, release, and reaction where relevant. Parallel actions are possible only when visually and physically compatible.
- Avoid stacking independent revelations, location changes, complex camera moves, and long speeches into one short request. Simplify staging or split the beat rather than compressing all events into rushed prose.
- Introduce a cut when it provides new information. Prefer camera movement for a minor reframing. No fixed shots-per-segment quota is required.

Do not end each generated segment with a dramatic resolution, musical fade, or neutral reset unless the film calls for it. Mid-scene segments should preserve momentum into the next segment.

## 3. Continuity and references

Maintain a compact **global continuity sheet** for stable facts: character appearance and clothing, voice identity, location layout and landmarks, key props, visual style, and lighting baseline. Do not repeat irrelevant off-screen facts inside every payload.

Maintain a **boundary state record** for changing facts. For each relevant segment entrance and exit, record:

| Category | Useful state |
| --- | --- |
| People | Position, facing, eyeline target, posture, active hand, expression/intention |
| Props | Holder, hand, location, orientation, open/closed, intact/broken, contents |
| Space and camera | Landmark relations, screen direction, camera side of the action axis, framing |
| Motion | Action phase, direction, momentum, what has already happened |
| Sound | Speaker and line completion, ambience, ongoing effect/music phase |

Only track categories that matter to the sequence. A downstream entrance must match the upstream exit or explicitly account for the change with a visible action, cutaway, elapsed time, or scene transition. A prop cannot silently switch hands, a closed door cannot become open, and an eyeline cannot reverse without a motivated change. Maintain an intelligible action axis; when crossing it is intentional, establish the new spatial relationship.

Choose the handoff deliberately:

- **Ordinary cut:** maintain compatible action, eyeline, and screen direction, while allowing a new composition. Exact frame matching is unnecessary.
- **Continuous-action handoff:** specify the exact action phase and camera state. Use a suitable actual endpoint frame/video as a reference when the workflow supports it. Do not replay the completed action in the next segment or assume text alone guarantees seamlessness.
- **Time/location change:** explicitly establish the new state and the narrative link; do not force false physical continuity.

For each segment choose the input mode from its actual inputs: T2VA for text; I2VA for an available first frame; FL2VA for available first and last frames with a feasible continuous path; L2VA for an available last frame; Ref2VA for the supported multi-reference relationships. Use the inherited mode guide for exact structure. A planned frame is a dependency, not an available asset. Never invent a usable file, reference video, or audio track. If a segment depends on an ungenerated predecessor, mark its prompt provisional and identify which boundary facts/reference slots must be resolved later.

Maintain a reference manifest mapping stable project identities to the actual assets supplied in each request. H3 `<Picture N>`, `<Video N>`, `<Audio N>`, and `<Subject N>` labels must resolve locally according to the selected guide and input order. Do not assume the model remembers a label from a previous request. Keep global character/voice identities in the planning sheet; assign local speaker `(Sx)` IDs according to the selected guide, with an explicit mapping back to those identities. The same character may have a different local number in another request; its appearance and voice must remain consistent.

Plan audio across the whole film. State which ambience continues, which effects conclude, and whether music is generated per clip or supplied as one editorial track. Repeating a music description does not guarantee sample-accurate continuity. Prefer line boundaries between separate speech generations when possible. If a line must cross a segment boundary, specify how the actual continuous audio will be supplied or edited; `<scenetrans>` documents a cut within a payload and does not by itself join separate generations. Distinguish a sound reference from direct reuse, and do not promise seamless audio without the necessary source or editing plan.

## 4. Standalone prompt packaging

Write each payload only after its duration, dramatic task, mode, references, and entrance/exit states are resolved or explicitly marked provisional.

For each prompt:

1. Establish the relevant stable visual and vocal facts, opening composition, and current dynamic state. Avoid phrases such as “same as before” or “continue the previous scene” without concrete details and supplied references.
2. Describe only this segment's observable actions, dialogue, camera changes, and synchronized sounds in playback order. Preserve required dialogue verbatim under the selected guide. Keep film-level explanation and future plot out of the payload.
3. Give local cut times where required. Match the amount of action and speech to the duration; more descriptive words do not create more available seconds.
4. Make the exit pose/action phase and unfinished sound clear when needed for the next segment. Do not mention nonexistent future assets or require the model to remember another prompt.
5. Apply the original base or Ref2VA fields, order, reference labels, and keyframe instructions unchanged. Planning tables, segment IDs, film timecodes, editorial trims, and continuity records stay outside the H3 payload.

For a request to write all prompts, deliver all segment payloads, not one example followed by “repeat similarly.” For planning-only or revision-only requests, provide only the requested deliverable. A revision should propagate to dependent entrance states, references, durations, and dialogue coverage when affected, without rewriting unrelated segments.

## 5. Delivery and review

Scale detail to the project. A multi-segment prompt package should expose these items compactly:

- Assumptions and workflow limits, with unresolved dependencies clearly marked.
- Global continuity sheet and reference manifest.
- Segment plan: ID; film interval; G; selected source interval; mode; dramatic task and shot progression; dialogue/action budget; entrance and exit states; next handoff; reference dependencies.
- Separate complete H3 payload for each requested segment, preceded by its ID, duration, mode, and local input mapping outside the payload.
- Assembly notes for trims, overlaps, sound continuity, and outstanding checks.

Review the plan and prompts together:

- All required story beats and exact dialogue are covered once unless repetition is intentional. Each consequence has a visible/audible cause or a clearly signaled ellipsis.
- Generated durations obey the known workflow constraints; kept intervals, overlaps, and additions reconcile with the requested film duration. Local cuts are strictly increasing and fall inside their segment.
- Dialogue, action, pauses, and reactions fit their allocated time. Essential content does not fall into discarded handles.
- Neighboring state records agree, or the transition explains the change. Check props, hands, eyelines, screen direction, and action phase.
- Every reference label resolves to the supplied local input; every unavailable dependency is explicit. Each payload can be understood independently.
- No accidental action replay, voice renumbering confusion, recurring music restart, or forced fade occurs at generation boundaries.

This is a planning check, not evidence that generated footage passes visual or audio review. If actual output becomes available, reconcile the next prompt with the observed endpoint, not merely the planned endpoint. If that endpoint violates an essential story fact, flag a repair/regeneration need rather than silently changing the story to accommodate it.

## 6. Worked planning example

Assumptions: a 36-second film, 4–15-second requests supported for the selected modes, ordinary cuts, no dialogue, no handles or overlaps. A woman finds a key inside a drawer, opens a locked box, then discovers a photograph. The drawer and box are established on the same desk; the box lock faces her. A character and room reference must be supplied for the Ref2VA segments below.

| ID | Film time | G / source selection | Mode | Task and shot progression | Entrance → exit | Handoff/dependency |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | 00:00–00:10 | 10s / [0,10) | Ref2VA | Establish the desk and box; open drawer; reveal key; take it | Drawer shut, both hands empty → drawer open, key in right hand, box still locked | Cut to lock detail; character/room references plus a usable exit frame from C01 for C02 |
| C02 | 00:10–00:24 | 14s / [0,14) | Ref2VA | Insert key; turn it; unlock; lift lid; pause at contents | Key in right hand → key left in lock, lid held open with left hand, right hand free | Cut to reaction/detail; use actual C01 state as reference, with new framing; actual C02 endpoint needed for C03 |
| C03 | 00:24–00:36 | 12s / [0,12) | Ref2VA | Lift photograph with right hand; look at it; hold reaction | Left hand holds lid, right hand free → photograph in right hand, lid still supported | End of film; use actual C02 state plus identity/location references |

The total is 10 + 14 + 12 = 36 seconds. C02 owns the unlocking action; C03 must not unlock the box again. The film's 00:10 timestamp never becomes C02's opening timestamp: its payload starts with `[Shot 1]` and its later cuts use local time. C02 and C03 remain provisional until their predecessor references exist. The plan does not claim a seamless one-shot continuation: each boundary is an intentional cut. If the user instead requests continuous framing, reconsider the handoff modes and references rather than merely changing the transition wording.
