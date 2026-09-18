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
  input/skill-map.json            the closed set of Technical Skills labels and the
                                  values under each. Authoritative for that section.
                                  Read at Step 2, applied at Step 5
  input/profile.md                shared and single-source: employers, dates,
                                  locations, education, contacts. The gate reads it
  input/master-resume-{track}.md  per-track: skills, certificates, open source,
                                  behavioural examples. Selected in Step 3
  input/projects.md               the shared project record: what was built, the
                                  skills each project used, and every metric
  input/quiz-{slug}.txt           optional. Read in Step 10 only, only if the user says yes
  scripts/resume_date.py          today's date in the resume location's timezone.
                                  Run at Step 1. Its answer is the only date this
                                  run may use, for the folder and the letter alike

Output:
  output/{YYYYMMDD}/{company}-{position}/{name}.md
  output/{YYYYMMDD}/{company}-{position}/{name}-cover-letter.md
  output/{YYYYMMDD}/{company}-{position}/jd.md   the posting, archived verbatim
                                  beside the deliverables. Never converted, never gated
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

1. **Batch every read into one message.** The JD, `track-map.json` and `skill-map.json`
   go together at Step 2; the primary track file, every secondary, `input/profile.md` and
   `input/projects.md` go together at Step 4. Never read a file twice in a run; hold what you read.
2. **Two shell commands per run.** `python scripts/resume_date.py --json` at Step 1 and
   `python scripts/verify_resume.py` at Step 6. Everything else is Read, Glob, Grep or
   Write. Never `ls`, `cat`, `head` or `mkdir`. The Write tool creates parent directories
   on its own.
3. **Do not narrate.** No phase announcements, no "now analysing the job description", no
   intermediate summaries of the JD or the track files, no printed plan. Work silently
   from Step 1 to Step 7, then print the report. The analysis in Steps 2 and 3 stays in
   your head; it is never written to chat or to a file.
4. **Write all three output files in one message.** The resume, the cover letter and
   `jd.md` are three Write calls issued together, not three rounds. The JD text is
   already in hand from Step 2, so archiving it costs no read.
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

- **Programming Languages**: Java (8, 11, 17), TypeScript, JavaScript, SQL
- **Frameworks & Libraries**: Spring Boot, Spring Data JPA, Hibernate, Angular, React

## Professional Experience

### Senior Full Stack Developer | 02/2024 - 03/2026 | Las Vegas, NV
#### NeoVegas Gaming Systems

One line on what this role built, for whom, and on what.

- One achievement per bullet.
- Another achievement.

#### Key Projects

- Player Wallet Service - what it does, and what the candidate built in it.
- Live Odds Dashboard - same shape, one line.

**Tech Stacks**: Python, FastAPI, PostgreSQL, Redis, React, Docker, AWS (EC2, S3)

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
- [ ] Inline bold appears **only** as a technical-skill row label or as the
      `**Tech Stacks**:` label closing an experience entry. Nowhere else
- [ ] Every experience entry runs summary line, bullets, `#### Key Projects`,
      `**Tech Stacks**:`, in that order, with nothing after the stack line
- [ ] Both sub-labels are spelled exactly `Key Projects` and `Tech Stacks`
- [ ] Every Tech Stacks value is evidenced: it appears on a `Skills used` line of
      a project belonging to **that** company. Never a `rules.unevidenced` value
- [ ] Sections present: Summary, Technical Skills, Professional Experience, Education
- [ ] Sections absent: Core Competencies, Key Skills, Core Skills, Leadership & Impact,
      Gap Analysis
- [ ] Every skill label is one of the nine in `input/skill-map.json`, spelled exactly as
      that file writes it. No invented, renamed or merged label
- [ ] 6 to 8 skill categories, and no value repeated across two rows
- [ ] Resume under 1050 words, target roughly 900. Cover letter under 430 words, target
      250 to 400
- [ ] Headline is one line, under 60 characters, and its distinctive words match `target-role`
- [ ] Every company, date, location, school and contact value appears verbatim in
      `input/profile.md`
- [ ] Every metric appears verbatim in a `Measured results` line in `input/projects.md`
- [ ] No project-specific date range: only the employing role's period is recorded

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

### The run date

```
python scripts/resume_date.py --json
```

Returns `{"letter": "September 10, 2026", "folder": "20260910", "timezone": "..."}`.

**This is the only date the run may use.** `folder` names the output directory at Step 7
and `letter` is the date line of the cover letter at Step 5, verbatim, including the
spelling and the absence of a leading zero on the day.

The date comes from the timezone of the **resume location** recorded in `input/profile.md`
section 4, not from the machine's clock and not from the session date you were told at the
start. Those two disagree whenever the machine sits in another timezone than the candidate,
and a letter dated a day ahead of the candidate's own calendar is a tell. Never substitute
your own idea of today, even when it looks right, and never reformat what the script
returns.

If the script exits non-zero it says what `input/profile.md` is missing, usually a
`- **Timezone:** <IANA name>` line for a state that spans two zones. **Stop** and report
that, the same as a missing JD.

## Step 2: Job description analysis

**Read `input/jd-{slug}.txt`, `input/track-map.json` and `input/skill-map.json` together,
in one batch.** The track map is needed at Step 3 and the skill map at Step 5, so reading
both here costs no extra round trip.

Hold the following, without writing any of it to chat:

- Company name. If genuinely absent, infer from domain or email clues, else use "the
  target company" and flag it in the report.
- **Job title, exactly as written.** This becomes `target-role` and drives the headline gate.
- Level, years required, must-have and nice-to-have skills as exact keywords, key
  technologies, certifications, domain expertise.
- The top 15 to 20 ATS keywords, ranked by importance and frequency. Note variants
  ("Kubernetes" / "K8s") so one mention covers both.
- **Soft requirements, as the exact strings the posting uses**: "excellent written and
  verbal communication", "strong analytical thinking", "attention to detail", "eagerness to
  learn", "collaborate with business analysts and stakeholders". These score as their own
  keyword category and land almost entirely in the summary, so capture the literal wording
  rather than a paraphrase. `input/soft-skills.md` holds what may be claimed against them.
- **Role responsibilities**: what the hire would actually spend time doing, as verbs plus
  objects. Take these from the responsibilities and day-to-day sections, not the skills
  list. Step 3 selects source files from these, so they matter more than the keyword list.

## Step 3: Track selection

There is no combined master resume. Each `input/master-resume-{track}.md` is the whole
record filtered to one kind of role: the skills list in Section 1, then certificates, open
source, and behavioural examples written specifically for that kind of role. The hard facts are **not** in these files. They are shared
and single-source in `input/profile.md`, with the project record in `input/projects.md`.
Track selection therefore decides what the resume may *claim*, which is what makes it the
highest-leverage step in the run.

`input/master-resume-bone.md` is the anonymised sharing template. Never read it, never
select it.

**`input/track-map.json`, read at Step 2, decides this step.** Its `tracks` object is
authoritative for which track files exist, so a track it does not list has no file and
cannot be selected. The file is data only; the algorithm is here. Work these steps in order,
reading the two thresholds from its `rules` object:

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
and which projects lead. The second widens the behavioural and certificate material only,
not the document's shape. Neither supplies facts, which come from `input/profile.md`
whatever the selection, and neither supplies the Technical Skills section, which comes from
`input/skill-map.json` alone. Track selection still orders that section: each category in
the skill map carries a `track_affinity` list, used to break ties between two categories
the posting weights equally.

Prefer the map over your own reading of the JD. It encodes what the record actually
supports, which is not the same as what the title suggests. If the map and the
responsibilities genuinely disagree, follow the map and log the disagreement at Step 8.

## Step 4: Read the sources

**One parallel batch of Read calls: the primary track file, every secondary,
`input/profile.md`, `input/projects.md`, `input/soft-skills.md` and `input/keywords.md`.**
Nothing else is read this run.

| Content | Comes from |
|---|---|
| Every fact: employers, titles, dates, locations, education, contacts | **`input/profile.md`**, the only source |
| Projects, what was built, and every metric | **`input/projects.md`**, the only source |
| Technical Skills rows | **`input/skill-map.json`**, the only source for labels and values |
| Soft-skill and competency wording for the summary | **`input/soft-skills.md`**, the only source |
| Practice and domain wording for bullets | **`input/keywords.md`**, bullets only, never a Technical Skills row |
| Certificates and open source, Sections 2 and 3 | **the primary track alone** |
| Behavioural examples, Section 4 | **the primary track alone.** Written per track on purpose, so the wording differs between files by design |

The two shared files are not per-track and are never duplicated into a track file, so there
is no primary-versus-secondary question for either: read each once and use it whatever the
selection. That is also why the old cross-track fact-drift rules are gone. A fact now exists
in exactly one place, so two files cannot disagree about it.

Each project entry carries a `Tracks` line, a `Skills used` line and a `Measured results`
line.

**`input/skill-map.json` is an inventory, not a shortlist.** It lists everything the
candidate can claim, grouped under nine fixed labels, and it is deliberately longer than any
resume can carry. **Select by JD relevance alone**, inside the eight-row budget, and let the
rest go. A value matching nothing in this posting does not go on the page, however
impressive it is. That is how an SAP architect resume ended up listing Rust, Scala, Dart and
SAS. Section 1 of the track files stays readable as background, but it no longer sets the
labels or the values.

**`Skills used` is the evidence line.** A skill listed in a project can be claimed at
project level: written into a bullet, tied to what was built. A skill listed in
`input/skill-map.json` but absent from every `Skills used` line has no project behind it, so
it belongs in Technical Skills and nowhere else. Never write a bullet around it. The map's caveats and
the library's "Recorded scope limits" both exist to catch this.

A project entry may also carry a **`Recorded gaps`** line. That names detail the project
genuinely lacks, usually specific tooling. Claim what the entry evidences and never what a
gaps line says is unrecorded: naming a vector store or a model the record does not confirm
is fabrication even when the project itself is real.

Rank projects by the `Tracks` line, primary first, then secondary, then the rest. A project
tagged for neither selected track can still supply a bullet when its `Skills used` matches
the JD; the tag orders the work, it does not gate it.

Score each role for relevance to the target (90-100 high, 60-89 medium, 0-59 low), and
note as you go the JD requirements nothing in the sources supports. That running list
feeds the report at Step 7 and the gaps log at Step 8. It never reaches the resume.

## Step 5: Generate

Write the resume and cover letter, then issue those two Writes together with the
`jd.md` archive described in Step 7, in a single message.

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

**Summary.** 60 to 110 words, or up to 130 when the posting lists six or more soft
requirements and the page budget allows. Years and primary expertise, then the specific
platform or domain overlap with this JD, then the delivery record that proves it. Lead with
what this employer is hiring for, not a generic self-description. The extra words are for
competency phrasing that has nowhere else to go, never for a longer technology list; the
1050-word resume budget is unchanged and still binds.

The summary is also the **only place soft keywords can land**, and they score as their own
category. Work in up to three of the posting's soft requirements, using the literal strings
captured at Step 2 and the phrasings `input/soft-skills.md` allows against them. Each must
be attached to something real: "collaborative" on its own is filler, while "worked the
validation rules out with the business users who sent the files" carries the same keyword
and survives a reading. Never assert a trait `input/soft-skills.md` lists under **Not
claimable**, however plainly the posting asks for it; log the miss at Step 8.

Industry terms belong here too. The sector itself cannot be changed, but name the honest
overlap: a regional bank is a regulated, audited environment with operations staff as
internal users, which is the real adjacency to insurance, fintech and enterprise postings.
Never write a domain tag the record does not support.

**Technical Skills.** Built entirely from `input/skill-map.json`, read at Step 2. Format
`- **Category Label**: value, value, value`.

The nine labels in that file are a **closed set**. Write them verbatim, ampersand and
capitalisation included. Never invent a label, never rename one to echo the posting's
wording, never merge two into one, and never split one in two. The point is that the
section reads the same way on every application instead of inventing a fresh taxonomy per
posting, which is the single clearest tell that a machine wrote the page.

Rendering it is four decisions, in this order:

1. **Which rows.** Nine categories, eight rows allowed, so at least one is always cut. Drop
   the categories this posting does not ask for, lowest JD relevance first, until six to
   eight remain. A category with no JD-relevant value is not rendered at all, whatever the
   row count: an empty or padded row is worse than a missing one.
2. **Row order.** Most JD-relevant first. Break ties with `track_affinity`, preferring the
   category that names the primary track, then with the order the file lists them in.
3. **Which values.** Inside each rendered row, keep only what this posting cares about,
   ordered by JD relevance. 8 to 16 values, or up to 18 on a posting dense enough to ask
   for them by name; a row listing 40 technologies reads as a keyword dump. Widen a row
   only for values the posting actually uses, never to spend the allowance.
4. **Check for repeats.** The file already places each value in exactly one category, so
   rendering it as written cannot repeat a value. Never restore a repeat by copying a value
   into a second row because the posting uses that wording. A resume naming Docker under
   both Cloud & DevOps and Tools & Platforms has failed this step.

Several categories carry a `recorded_gaps` line. Honour it: it names what the row may **not**
say, however hard the posting pushes. `Data & AI` records AI as capability only, so no model
provider, vector store, framework or AI metric may appear; `Testing` may not name Cypress,
Playwright, Pact or WireMock. `Methodologies` is the one gap that limits placement rather
than listing: `Agile / Scrum` and the ceremony names may be rendered in the Technical Skills
row under the `no_invention` rule, but no bullet and no summary sentence may claim to have
practised or facilitated them. Never add a value to close a gap the file declares, and log
any gap that cost real JD coverage at Step 8.

**Professional Experience.** Every role from the employment table in `input/profile.md`
Section 1, real titles unchanged. Each entry is **four parts in a fixed order**, and
`verify_resume.py` blocks the build if any is missing or out of order:

```markdown
### Senior Full Stack Software Engineer | 06/2024 - Present | Clayton, MO, USA
#### Centene

<summary line>

- <achievement bullet>
- <achievement bullet>

#### Key Projects

- <Project Name> - <what it does and what was built in it>

**Tech Stacks**: <the stack this company's projects actually used>
```

The point of the shape is that a reader scanning the page finds the same thing in the same
place under every employer: what the role was, what it achieved, what it shipped, what it
was built on. Both sub-labels are fixed strings. Never rename them to echo the posting.

**1. Summary line.** One plain sentence, 20 to 35 words, no bullet marker and no bold.
What this role built, for whom, and on what. It is the entry's headline, so lead with the
part of the role closest to the posting: the same job reads as platform work on an
infrastructure JD and as product delivery on a product one. Never a duty list, and never a
restatement of the document summary.

Good: `Built member and case management services and an internal AI assistant for the
operations staff running government-sponsored health plans.`
Bad: `Responsible for full stack development, code review and production support.`

**2. Achievement bullets.** 3 to 5 per role, most JD-relevant first, down from the old 4 to
6 because the entry now carries three other parts. Build them from the `input/projects.md`
entries belonging to that company: the prose says what was built, and `Measured results`
holds the only numbers that may appear. Bullet shape: what you did, what you built or
changed, what happened as a result. Strong verb first, a real number where `Measured
results` has one. Screeners look for about five quantified outcomes across the page; use
every real number before falling back to qualitative phrasing, and never close the gap by
inventing one. Leadership belongs here, in the role where it happened, not in its own
section.

Good: `Owned production support for live systems, investigating and resolving complex
defects, shipping enhancements and improving application responsiveness by 30%.`
Bad: `Worked on performance improvements.`

**3. Key Projects.** 2 to 3 per role, one line each, as `- Project Name - what it does and
what the candidate built in it`. Names come verbatim from the `###` headings of
`input/projects.md` under that company, so the resume and the record use one name for one
thing. Select by `Tracks` line first, then by which `Skills used` lines match the posting.
A role with only one recorded project lists one. Never invent a project, never merge two
into a portmanteau, and never repeat a bullet's sentence here: the bullet says what changed,
the project line says what the thing is.

A project link is allowed only where `input/projects.md` records a real URL. Write it bare
(`github.com/org/repo`), never as a markdown link and never as a link glyph: square brackets
and emoji are both blocking gate failures.

**4. Tech Stacks.** One line, `**Tech Stacks**: value, value, value`, 10 to 18 values, most
JD-relevant first. This is the one line in the document tied to a specific employer, which
makes it the easiest place in the whole resume to fabricate, so it has its own evidence
rule, stricter than the Technical Skills section:

- Every value must appear on a `Skills used` line of a project belonging to **that
  company**. Technical Skills may render a `rules.unevidenced` value from
  `input/skill-map.json`; a Tech Stacks line may never, because listing it under an employer
  claims it was used there.
- Repeating values already in Technical Skills is correct and expected. The two sections
  answer different questions: what the candidate can do, and what this job was built on.
  The `no_duplicate_values` rule governs rows inside Technical Skills, not this line.
- Write the names as `input/skill-map.json` spells them where it carries the value, so one
  technology reads the same way everywhere on the page.
- Order by JD relevance, not by the order `input/projects.md` happens to list them.

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
project and metric must already appear in it. The `letter` date from Step 1 exactly as the
script printed it, `Hiring Manager` or a named contact,
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

Then read once more for what the gates cannot see: most relevant experience first, and
no sentence that sounds like a press release. Facts need no cross-checking any more:
`input/profile.md` is their only source, and the gate reads it.

**Coverage sweep.** The gates count words and rows; they cannot tell whether this posting's
language reached the page. ATS scoring splits into three categories, so sweep all three,
once, before delivering. Take the lists captured at Step 2.

| Category | Check | Where it should land |
|---|---|---|
| **Hard** | Every must-have technology appears as the posting's literal string | Skills row, and a bullet where `Skills used` allows one |
| **Soft** | Up to three of the posting's competency phrases appear | Summary, attached to something concrete |
| **Industry** | The sector, or the nearest honest adjacency, and the posting's process vocabulary appear | Summary and bullets |

Two failure modes to look for specifically:

- **A buried must-have.** A required keyword sitting only in the Technical Skills row is
  matched but weakly placed. If `input/projects.md` carries it on a `Skills used` line, work
  it into the bullet for that project. If it does not, leave it in the row alone: that is
  the evidence rule, not a defect, and Step 8 logs it.
- **A silent category.** A summary with no competency phrase scores near zero on Soft
  however strong the bullets are, because Soft has nowhere else to land.

**One revision pass, then stop.** Fix what the sweep names, re-run the gates once, and
deliver. The sweep may only re-word and re-place material the record already supports.
It may never add a claim, and it may never narrow the keyword list until the number looks
better: an unmet requirement is reported at Step 7, not written around. If a second pass
looks necessary, the gap is in the record, not the wording, and it belongs in
`data/{slug}/master-resume-gaps.md`.

## Step 7: Deliver

All three files go to `output/{YYYYMMDD}/{company}-{position}/`, each path component
lowercased with non-alphanumeric runs collapsed to hyphens. `{YYYYMMDD}` is the `folder`
value from Step 1, so the directory and the letter always carry the same day. The Write
tool creates the folder.

| File | Contents |
|---|---|
| `{name}.md` | the tailored resume |
| `{name}-cover-letter.md` | the cover letter |
| `jd.md` | the posting this run was written against, archived verbatim |

**`jd.md`** keeps the application folder self-contained: months later the folder still
records what the resume was aimed at, without depending on `input/jd-{slug}.txt`, which the
next run overwrites. Write the header below, then the **unmodified** text of
`input/jd-{slug}.txt`, byte for byte, from what was read at Step 2.

```markdown
<!--
target-company: Accuris
target-role: SAP Solution Architect
kind: jd
source: input/jd-accuris.txt
run-slug: accuris
archived: 2026-08-01
-->

# SAP Solution Architect - Accuris

<the job description, exactly as it appeared in input/jd-{slug}.txt>
```

This file is source material, not a deliverable. **None of the CONTRACT or CHECKLIST rules
apply to it:** leave the posting's em dashes, bullet glyphs, brackets and banned phrasing
exactly as the employer wrote them. Never edit, summarise, reformat or truncate it. The
verifier never reads it and `convert_resume.py` skips it when resolving a folder, so it
never affects a gate or a PDF.

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
  to Section 2 of each track file to include it next run.]
```

Then the handoff, with the real path filled in. The conversion command is the last line of
the handoff block, but not the last line of the turn: the Step 9 ATS score goes under it,
and the Step 10 question under that.

```
Resume and cover letter are ready.

- Resume: [path]
- Cover letter: [path]
- Job description (archived): [path]

Before submitting:
1. Verify every achievement and date reads true to you.
2. Read the cover letter aloud, and adjust the tone if it does not sound like you.

python scripts/convert_resume.py "{YYYYMMDD}/{company}-{position}/{name}"
```

That command converts both files: it finds the paired `-cover-letter.md` automatically.
The user runs it themselves; this skill never runs it for them.

Nothing in this step is printed until the Step 9 checker has already run. See Step 9.

## Step 8: Deferred logging

The deliverable is done. Now record what would make the next run better, in
`data/{slug}/new-skills.md` and `data/{slug}/master-resume-gaps.md`.

**This is one Grep call and at most two Writes.** Read `logging.md` for the entry formats
and the classification rules. Nothing found here changes the files written at Step 7.

## Step 9: ATS check

The deliverable and the logs are done. Run the `resume-ats-checker` skill against the
folder just written, in minimal mode:

```
/resume-ats-checker output/{YYYYMMDD}/{company}-{position} --min
```

It resolves the resume and `jd.md` from that folder on its own, so pass the folder and
nothing else.

**Invoke the checker before printing anything from Step 7.** Invoking a skill interrupts
the turn, so a checker run issued after the summary has been printed puts its score
*above* the summary, which is the wrong end of the report. The order that works is: write
the files at Step 7, log at Step 8, invoke the checker here, and only then print the
Step 7 summary and handoff, followed by the score.

The score is the **last block before the Step 10 question**, on its own under an `**ATS**:`
label, directly under the handoff's conversion command:

```
**ATS**: ATS Compatibility: 95%   Keyword Match: 66%  (Hard 67% / Soft 57% / Industry 57%)   [BELOW 80%]
```

One line, plus at most one sentence naming what held the number down. Nothing else goes
between it and the question.

**This is a measurement, not a gate.** It runs after Step 7 has already shipped the files,
and it is read-only by design. Whatever it scores:

- Never edit, regenerate or re-verify the resume or cover letter in response to it
- Never re-run it a second time hoping for a better number
- Never expand it to the full report unless the user asks for it by name
- A score below 80% is reported and left alone. Acting on it is the user's call, and the
  way to act on it is a fresh run against a revised track file, not a patch to this output

If the checker cannot resolve the pair, say so in one line in that same last position and
continue to Step 10. A failed check never blocks delivery, which already happened two
steps ago.

## Step 10: Post-delivery questions

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
