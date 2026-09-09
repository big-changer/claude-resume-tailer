# Edge Cases

Read this only when one of these conditions actually fires. The normal run never needs it.

## Inputs and run context

| Scenario | Action |
|---|---|
| The skill was invoked with no slug | One `jd-*.txt` present: use its slug and say so in the report. Several: stop and ask which. None: stop |
| `input/jd-{slug}.txt` missing | Stop and report the path checked. The only condition that halts a run |
| Only another slug's `jd-*.txt` exists | Do not read it. Treat as missing |
| Sessions running at once | Each is invoked with its own slug, reads its own `input/jd-{slug}.txt`, and appends under its own `data/{slug}/`. Read before appending |
| `data/{slug}/` does not exist | The Write tool creates it. Never skip a log write because the directory is missing |
| Company name unresolvable from the JD | Use "the target company", same placeholder in the cover letter recipient, and flag it in the report |

## Track selection

| Scenario | Action |
|---|---|
| JD spans several kinds of work | Two tracks at most, ranked. The primary drives the document and supplies every fact |
| No track matches the JD | Use `master-resume-fs.md` as primary and log it to the gaps file. The map's "no track fits" list names the disciplines this covers |
| The map names a track whose file is missing | Treat it as "no track fits" and fall back to `fs`. Log it: the map and the files have drifted apart |
| A `master-resume-*.md` file exists that the map does not list | Do not select it. The map is authoritative. Log it so the map can be updated |
| The map and the JD's responsibilities disagree | Follow the map, which encodes what the record supports rather than what the title suggests. Log the disagreement |
| Two track files contradict each other on a fact | Facts follow the primary track. Log the drift |
| A secondary track has a fact the primary lacks | Do not use it. The frozen-facts gate would pass it, which is exactly why the rule is here. Log the drift |
| Section 2 core skills are irrelevant to this JD | Prefer them within the eight-category budget, but do not blow the budget to include them all |
| Two sessions both need a master resume sync write | The track files are shared, so apply one edit at a time and re-read the file before the second write |

## Content and gaps

| Scenario | Action |
|---|---|
| JD names a tech skill not in any track file | Log it to the new-skills file at Step 8. Do not use it this run. Do not ask |
| Skill missing but adjacent to a recorded one | Bridge via the closest adjacent skill, else omit and flag in the report and gaps file |
| The candidate clearly does not qualify | Still generate, honestly and without inflation. Log why in the gaps file. Never refuse and never ask |
| Junior candidate, senior posting | Do not inflate the headline. Use the title without the inflated seniority word and highlight relevant depth |
| Combination role | Prioritise the primary, keep the secondary visible in skills |
| Missing metric | Honest qualitative phrasing or a clearly scoped estimate. Never a fabricated number. Flag any estimate in the report |
| Fewer than five quantified results exist | Report the shortfall and name the specific bullets that would carry a number. Do not invent one |
| JD requires a certification the candidate lacks | Omit it. Report as an unmet requirement. Never generate one |
| A track file records a credential but not its details | Omit the entry, report exactly what to add to close it. This applies even when the track file's own notes ask for a bracketed placeholder: omission achieves what those notes want without shipping an unsubmittable placeholder |
| A degree is missing its discipline, institution or year | Same rule as a credential: omit and report |
| User supplies a real fact mid-session | Apply the master resume sync rules in `logging.md`, then use it |

## Output and gates

| Scenario | Action |
|---|---|
| Resume runs over two pages | Cut the least JD-relevant skill categories first, then the weakest bullet in each role, then optional sections |
| A gate fails | Fix only what it names and re-run once. Do not use `--no-verify`, and do not re-read the track files to fix a style gate |
| The frozen-facts gate passes but a fact came from an unselected track | The gate reads the union of all track files, so it cannot catch this. Check it by reading, and replace the value with the primary track's version |

## Step 9 questions

| Scenario | Action |
|---|---|
| User answers `y` but `input/quiz-{slug}.txt` does not exist | Report the exact path to create, in one line, and stop. No fallback file, no glob, no "paste them instead" |
| `input/quiz-{slug}.txt` exists but is empty | Same as missing |
| Only another slug's `quiz-*.txt` exists | Do not read it. Treat as missing |
| Quiz file has no numbering or punctuation | Parse it anyway: bullets, blank-line blocks or one per line all count. A question mark is not required |
| User says `y` again after a batch | Re-read the file, answer only the questions not yet answered this session, and say how many were skipped |
| User pastes questions in chat instead of using the file | Answer them in the same fenced format. Do not insist on the file |
| A question needs a fact nobody recorded | Honest one-liner in the fenced block, then say what you need after the list. Do not guess, especially on anything legal or contractual |
