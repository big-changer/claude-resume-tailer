---
name: resume-jd-optimizer
description: Use when tailoring a resume and cover letter to one specific job description - selects the matching per-track master resumes, generates a two-page resume plus cover letter that pass blocking build gates on the first try, and defers all bookkeeping until after the deliverable ships
---

# Resume-JD Optimizer

## Overview

Turns a job description plus the candidate's per-track master resumes into a tailored
two-page resume and a matching cover letter, both of which read as if a person wrote them.

**Core principle:** Truth-preserving optimization. Reorder, reframe and select from what
the track files already record. Never invent experience, dates, titles, certifications or
metrics.

**Second principle: the deliverable comes first.** The resume and cover letter are written,
verified and handed over before the skill does any logging, any skill detection, or any
reporting beyond the summary. Nothing in this workflow stops to ask a question until the
files exist on disk.

## When to Use

- The user has a job description in `input/jd-{slug}.txt` and wants a tailored resume.
- The user invokes `/resume-jd-optimizer {slug}`.

**DO NOT use for:** writing a resume from scratch with no master resume library, LinkedIn
profile work, or editing the track files directly.

## Quick Start

```
Input:
  input/jd-{slug}.txt             the posting. One per run slug
  input/track-map.json            JD text to track files. Authoritative for which
                                  tracks exist. Read at Step 2, applied at Step 3
  input/master-resume-{track}.md  the only resume sources. Each is complete on its
                                  own: skills AND facts. Selected in Step 3
  input/quiz-{slug}.txt           optional. Read in Step 9 only, only if the user says yes

Output:
  output/{YYYYMMDD}/{company}-{position}/{name}.md
  output/{YYYYMMDD}/{company}-{position}/{name}-cover-letter.md
  data/{slug}/new-skills.md            appended after delivery, never asked about
  data/{slug}/master-resume-gaps.md    appended after delivery, never asked about
```

The markdown is rendered by `scripts/convert_resume.py`, which refuses to write a PDF
unless the file passes every gate in `scripts/verify_resume.py`. **Those gates are the
real specification.** The CONTRACT and CHECKLIST sections below exist to produce a file
that passes them on the first try.

## Implementation

See supporting files, and read them only when the step says to:

| File | Read it |
|---|---|
| `output-contract.md` | Once, before writing the first output file, if the inline CONTRACT below leaves anything unclear |
| `house-style.md` | When writing prose, or when the human-style gate fails |
| `logging.md` | At Step 8 only, after both deliverables exist |
| `edge-cases.md` | Only when an unusual condition fires |

---

# SPEED RULES

This skill was rewritten because it was slow. The rules below are what made it fast, and
they matter as much as the content rules.

1. **Batch every read into one message.** The primary track file and every secondary are
   read in a single parallel batch at Step 4. Never read a file twice in a run; hold what
   you read.
2. **One shell command per run.** `python scripts/verify_resume.py` at Step 6 is the only
   one. Everything else is Read, Glob, Grep or Write. Never `ls`, `cat`, `head` or `mkdir`.
   The Write tool creates parent directories on its own.
3. **Do not narrate.** No phase announcements, no "now analysing the job description", no
   intermediate summaries of the JD or the track files, no printed plan. Work silently
   from Step 1 to Step 7, then print the report. The analysis in Steps 2 and 3 stays in
   your head; it is never written to chat or to a file.
4. **Write both output files in one message.** The resume and the cover letter are two
   Write calls issued together, not two rounds.
5. **Write against the CHECKLIST the first time.** Every gate failure costs a full
   read-fix-verify cycle. Check the list before the Write, not after the failure.
6. **All bookkeeping happens after delivery.** Skill detection and gap logging are Step 8,
   after the user already has the files. They never gate the deliverable, and their
   findings are never used in this run's output.
7. **Never stop to ask.** The one exception is a missing or ambiguous job description at
   Step 1. Uncertainty goes to `data/{slug}/master-resume-gaps.md` at Step 8, not to a
   prompt.

---

# CONTRACT

The markdown is parsed structurally. Emit exactly this shape:

```markdown
<!--
target-company: Accuris
target-role: SAP Solution Architect
kind: resume
-->

# Gafari Arowojebe
SAP Solution Architect
arowojebe.gafari.1127@gmail.com | +1 (224) 423-5835 | North Platte, NE (Remote)
linkedin.com/in/gafari-arowojebeg | github.com/codetechie-G

## Summary

One paragraph, or two at most.

## Technical Skills

- **SAP Platform**: SAP ECC 6.0, SAP HANA, FI/CO, SD/MM
- **ABAP and Integration**: ABAP reports, IDoc interfaces, SAP BTP, SAP CPI

## Professional Experience

### Senior Full Stack Developer | 02/2024 - 03/2026 | Las Vegas, NV
#### NeoVegas Gaming Systems

- One achievement per bullet.
- Another achievement.

## Education

### BSc. in Computer Science | 07/2012 - 05/2017 | St. Paul, MN
#### University of St. Thomas

Relevant coursework: Machine Learning, Data Structures, Algorithms

## Certifications

- AWS Certified Solutions Architect, Associate (2023)
```

The cover letter uses the same header block with `kind: cover`, then date, recipient,
salutation, body paragraphs and sign-off as plain prose. No sections, no bullets.

Full renderer semantics are in `output-contract.md`. The short version: dates are always
`MM/YYYY - MM/YYYY`, URLs are bare (`linkedin.com/in/handle`, never a markdown link),
blank lines and `---` are ignored, and there are no tables, no emoji and no HTML beyond
the metadata comment.

---

# CHECKLIST

Verify this list against the draft **before** the Write call. Each line is a blocking gate.

- [ ] No em dash, en dash, arrow, ellipsis character, curly quote or bullet glyph
- [ ] No square brackets anywhere, for any reason
- [ ] No banned AI phrasing: leverage, delve, seamless, robust and scalable, spearhead,
      cutting-edge, showcase, underscore, pivotal, meticulous, synergy, testament to,
      state-of-the-art, at the forefront, furthermore, moreover, not only, myriad, realm of
- [ ] Inline bold appears **only** as a technical-skill row label. Nowhere else
- [ ] Sections present: Summary, Technical Skills, Professional Experience, Education
- [ ] Sections absent: Core Competencies, Key Skills, Core Skills, Leadership & Impact,
      Gap Analysis
- [ ] 8 or fewer skill categories, every label 26 characters or fewer
- [ ] Resume under 1050 words, target roughly 900. Cover letter under 430 words, target
      250 to 400
- [ ] Headline is one line, under 60 characters, and its distinctive words match `target-role`
- [ ] Every company, date, location, school and contact value appears verbatim in the
      primary track file

---

# WORKFLOW

## Step 1: Run context

Several sessions share this checkout, so the posting and every file written outside
`output/` is namespaced by a **run slug**, which is the argument the skill was invoked
with. Lowercase it and collapse non-alphanumeric runs to single hyphens. **Never derive it
from the directory, branch, worktree or JD contents:** two sessions would resolve those
identically and overwrite each other.

No argument passed: Glob `input/jd-*.txt`. Exactly one, use its slug and say so in the
report. More than one, **stop** and ask which. None, **stop**.

The JD is `input/jd-{slug}.txt`. If it does not exist, **stop** and report the path
checked. This is the only condition that halts a run. Never read another slug's
`jd-*.txt`, even when the expected one is missing, and there is no `input/jd.txt` fallback.

## Step 2: Job description analysis

**Read `input/jd-{slug}.txt` and `input/track-map.json` together, in one batch.** The map is
needed at Step 3, so reading it here costs no extra round trip.

Hold the following, without writing any of it to chat:

- Company name. If genuinely absent, infer from domain or email clues, else use "the
  target company" and flag it in the report.
- **Job title, exactly as written.** This becomes `target-role` and drives the headline gate.
- Level, years required, must-have and nice-to-have skills as exact keywords, key
  technologies, certifications, domain expertise.
- The top 15 to 20 ATS keywords, ranked by importance and frequency. Note variants
  ("Kubernetes" / "K8s") so one mention covers both.
- **Role responsibilities**: what the hire would actually spend time doing, as verbs plus
  objects. Take these from the responsibilities and day-to-day sections, not the skills
  list. Step 3 selects source files from these, so they matter more than the keyword list.

## Step 3: Track selection

There is no combined master resume. Each `input/master-resume-{track}.md` is the whole
record filtered to one kind of role, **complete on its own**: skills in Sections 1 and 2,
every fact in Sections 3 to 15. Track selection decides both what the resume may claim and
what it is verified against, so it is the highest-leverage step in the run.

`input/master-resume-bone.md` is the anonymised sharing template. Never read it, never
select it.

**`input/track-map.json`, read at Step 2, decides this step.** Its `tracks` object is
authoritative for which track files exist, so a track it does not list has no file and
cannot be selected. Follow its `rules` object in order:

1. **`no_fit`.** If any `no_fit.keywords` entry appears in the title or must-haves, use
   `no_fit.fallback_track` as primary with no secondary, log `no_fit.log`, and stop here.
2. **Title.** The first track whose `titles` matches the JD title is the **primary**. This
   resolves most postings. It does not settle the secondary.
3. **Secondary.** Use the primary's `default_secondary` when it is set. When it is `null`,
   score every other track by counting its `keywords` in the JD's must-haves and take the
   best, provided it reaches `rules.min_keyword_hits`. Otherwise run with the primary alone.
4. **No title match.** Score all tracks, apply `domain_boost`, highest is primary, second
   only if it clears `rules.secondary_threshold` times the primary's score.
5. **Caveats.** Check the primary's `caveats` and every `global_caveats` entry. A caveat
   never blocks the selection: `action: select_anyway` means select the track, keep the
   named thing out of the resume, and write its `log` text to the gaps file at Step 8.

**Matching is on word boundaries, never bare substring.** `erp` must not match inside
"enterprise", and `ai` must not match inside "maintain". Multi-word entries match as phrases.

Never more than two tracks. The first is **primary**: it drives the headline, the summary,
the skill category ordering and **every fact in the output**. The second contributes skills
only, and exists to widen Sections 1 and 2, not to reshape the document.

Prefer the map over your own reading of the JD. It encodes what the record actually
supports, which is not the same as what the title suggests. If the map and the
responsibilities genuinely disagree, follow the map and log the disagreement at Step 8.

## Step 4: Read the sources

**One parallel batch of Read calls: the primary track file and every secondary.** Nothing
else is read this run.

| Content | Comes from |
|---|---|
| Skills, Sections 1 and 2 | **every selected track**, unioned, primary's wording winning on duplicates |
| Every fact: companies, titles, dates, locations, education, contacts, certifications, Sections 3 to 15 | **the primary track alone, always** |

If a secondary track holds a fact the primary does not, **do not import it.** The
frozen-facts gate reads the union of all track files so it would pass, but the files
disagreeing is drift. Use the primary's version and log the disagreement at Step 8.

Section 2, "Always-Required / Core Skills", is the candidate's standing declaration of how
they want to be positioned. Prefer those skills inside the eight-category budget, but the
two-page budget wins: do not carry every Section 2 entry into every resume regardless of
relevance. That is how an SAP architect resume ended up listing Rust, Scala, Dart and SAS.

Score each role for relevance to the target (90-100 high, 60-89 medium, 0-59 low), and
note as you go the JD requirements nothing in the sources supports. That running list
feeds the report at Step 7 and the gaps log at Step 8. It never reaches the resume.

## Step 5: Generate

Write the resume and cover letter, then issue both Write calls in a single message.

**Gaps resolve autonomously.** No shortfall stops the run.

| Shortfall | Resolution |
|---|---|
| Missing skill with no trace in any track file | Omit. Bridge to a closely adjacent recorded skill where one exists (resume has Kubernetes, JD wants Helm) |
| Missing metric | Honest qualitative phrasing, or a conservative estimate only where surrounding text implies a range. Never invent a number |
| Missing certification | **Omit the entry entirely.** Never generate a credential, never emit an AI-generated marker, never leave a placeholder |
| The JD's core requirement is something the candidate lacks | Still generate. Lead with the strongest genuine overlap, do not inflate, log it as a hard mismatch |

**Headline.** The JD's job title verbatim, or as close as the candidate's real seniority
allows. One line, no pipes, no module or technology list, under 60 characters. Must match
`target-role`. Good: `SAP Solution Architect`. Bad: `SAP Solution Architect | FI/CO &
Order Management (SD/MM) on ECC 6.0 / HANA | ABAP Development, IDoc & SAP BTP/CPI`.

**Summary.** 60 to 110 words. Years and primary expertise, then the specific platform or
domain overlap with this JD, then the delivery record that proves it. Lead with what this
employer is hiring for, not a generic self-description.

**Technical Skills.** One skills section, six to eight categories. Format
`- **Category Label**: value, value, value`. Labels 26 characters or fewer, short and
concrete, named for what this employer cares about ("SAP BASIS and Security", not
"Enterprise Platform Ecosystem"). Order categories and values by JD relevance. 8 to 16
values per category; a category listing 40 technologies reads as a keyword dump.

**Professional Experience.** Every role from the primary track's Section 3, real titles
unchanged. 4 to 6 bullets each, most JD-relevant first. Bullet shape: what you did, what
you built or changed, what happened as a result. Strong verb first, a real number where
the sources have one. Screeners look for about five quantified outcomes; use every real
number before falling back to qualitative phrasing, and never close the gap by inventing
one. Leadership belongs in the bullets of the role where it happened, not in its own
section.

Good: `Owned production support for live systems, investigating and resolving complex
defects, shipping enhancements and improving application responsiveness by 30%.`
Bad: `Worked on performance improvements.`

**Education and Certifications.** Complete entries only, per the missing-certification
rule above. Coursework as one plain line under the entry when relevant. Open source and
publications only when the JD makes them relevant and the page budget allows; they are the
first thing to cut.

**Literal keyword coverage.** Scanners match strings, not meaning. Write the exact string
the JD uses at least once for every must-have and industry tag. Naming AWS does not cover
"cloud"; naming LangChain does not cover "artificial intelligence". Give both spelled-out
and acronym forms on first use, and say years in digits ("9+ years"). Details and the
worked failure cases are in `house-style.md`.

**Cover letter.** Generated from the finished resume, not from scratch: every claim,
project and metric must already appear in it. Date, `Hiring Manager` or a named contact,
salutation, a 2 to 3 sentence opening naming the exact role with one hook, 1 to 2 body
paragraphs carrying 2 to 3 concrete achievements chosen against the must-haves, a closing
with one concrete detail about this company from the JD and an interview call to action,
then `Sincerely,` and the full name. 250 to 400 words, first person, active voice, same
house style. A letter generic enough to send unmodified to another company has failed.

## Step 6: Verify

```
python scripts/verify_resume.py {YYYYMMDD}/{company}-{position}/{name}
```

Five blocking gates: human style, frozen facts, headline, emphasis budget, structure and
length. `convert_resume.py` runs the same gates plus a page-count check and writes no PDF
if any fails.

Fix the markdown until they pass. **Never reach for `--no-verify`**; that flag is for
inspecting a work-in-progress layout, not for shipping. If a gate fails, fix only what it
names and re-run once. Do not re-read the track files to fix a style gate.

Then read once more for what the gates cannot see: every must-have keyword present and
none more than three times, every fact traceable to the **primary** track specifically
(the gate reads the union, so it will not catch a fact borrowed from an unselected track),
most relevant experience first, and no sentence that sounds like a press release.

## Step 7: Deliver

Both files go to `output/{YYYYMMDD}/{company}-{position}/` as `{name}.md` and
`{name}-cover-letter.md`, each path component lowercased with non-alphanumeric runs
collapsed to hyphens. The Write tool creates the folder.

Report in chat, not in the files:

```
## OPTIMIZATION SUMMARY

**Target**: [Company] - [Position] - [Level]
**Run slug**: [slug, and "(inferred: only one jd-*.txt present)" if it was not passed]
**Tracks used**: [primary (facts source), then any secondary]

### Coverage
- Must-have keywords covered: [X/Y]
- Nice-to-have keywords covered: [X/Y]
- Resume length: [N] words

### Not claimed
- [keyword] - [why, and what would close it]

### Omitted for missing detail
- [e.g. SAP certification: recorded as held, but no name, module, date or ID. Add those
  to Section 12 to include it next run.]
```

Then the handoff, with the real path filled in as the literal last line:

```
Resume and cover letter are ready.

- Resume: [path]
- Cover letter: [path]

Before submitting:
1. Verify every achievement and date reads true to you.
2. Read the cover letter aloud, and adjust the tone if it does not sound like you.

python scripts/convert_resume.py "{YYYYMMDD}/{company}-{position}/{name}"
```

That command converts both files: it finds the paired `-cover-letter.md` automatically.
The user runs it themselves; this skill never runs it for them.

## Step 8: Deferred logging

The deliverable is done. Now record what would make the next run better, in
`data/{slug}/new-skills.md` and `data/{slug}/master-resume-gaps.md`.

**This is one Grep call and at most two Writes.** Read `logging.md` for the entry formats
and the classification rules. Nothing found here changes the files written at Step 7.

## Step 9: Post-delivery questions

Ask exactly this, as the last line, and wait:

```
Any additional questions to answer? (y/n)
```

On yes, read `input/quiz-{slug}.txt` and answer its questions in the fenced format
described in `house-style.md`. On no, stop and do not ask again this session. If the file
is missing or empty, say so in one line with the exact path to create, and stop: no
fallback file, no glob, no request to paste them instead.

---

# CORE CONSTRAINTS

**No fabrication.** Never invent experience, dates, companies, titles, certifications or
metrics. Never claim a JD-only skill; detecting one and logging it is not evidence the
candidate has it. Reorder, reframe and select from existing content, nothing more.

**Never block.** Produce both deliverables on every run. The sole exception is a missing
job description, which is a missing input rather than an uncertainty. Uncertainty goes to
the gaps log at Step 8, not to a prompt.

**Authenticity.** Do not distort an achievement to fit the JD, and do not oversell impact.
What the candidate cannot defend in a technical screen does not go on the page.

**Honesty about gaps.** Unmet requirements are reported every run, never hidden behind a
keyword list narrowed until it scores 100%. A resume that scores 80% honestly beats one
that scores 100% against keywords the candidate cannot defend.

Unusual conditions are in `edge-cases.md`. Read it only when one fires.
