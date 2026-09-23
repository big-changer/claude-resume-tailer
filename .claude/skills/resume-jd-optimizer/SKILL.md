---
name: resume-jd-optimizer
description: Use when tailoring a resume and cover letter to one specific job description - reads the single master resume, generates a two-page resume plus cover letter that pass blocking build gates on the first try, and defers all bookkeeping until after the deliverable ships
---

# Resume-JD Optimizer

## Overview

Turns a job description plus the candidate's master resume into a tailored two-page resume
and a matching cover letter, both of which read as if a person wrote them.

**Core principle:** Truth-preserving optimization. Reorder, reframe and select from what
the record already holds. Never invent experience, dates, titles, certifications or
metrics.

**Third principle: every skill this posting names reaches the page.** A required
technology the record cannot evidence is still written into the Technical Skills row, as
the posting's own literal string, because a resume that never contains the word "Java" is
filtered by the ATS before a human reads it. What evidence controls is *where* a skill may
appear, not whether it appears at all: an unevidenced skill is listed, never claimed. The
tiering that enforces that split is at Step 5, and the aim is 100% of the posting's
required hard skills present on the page.

**Second principle: the deliverable comes first.** The resume and cover letter are written,
verified and handed over before the skill does any logging, any skill detection, or any
reporting beyond the summary. Nothing in this workflow stops to ask a question until the
files exist on disk.

## When to Use

- The user has a job description in `input/jd-{slug}.txt` and wants a tailored resume.
- The user invokes `/resume-jd-optimizer {slug}`.

**DO NOT use for:** writing a resume from scratch with no master resume, LinkedIn
profile work, or editing the master resume directly.

## Quick Start

```
Input:
  input/jd-{slug}.txt             the posting. One per run slug
  input/track-map.json            caveats only: what this record cannot claim, and
                                  what to log when a posting asks for it. Read at
                                  Step 2, applied at Step 3
  input/skill-map.json            the closed set of Technical Skills labels and the
                                  values under each. Authoritative for that section.
                                  Read at Step 2, applied at Step 5
  input/profile.md                single-source: employers, dates, locations,
                                  education, contacts. The gate reads it
  input/master-resume.md          the one master resume: skills, certificates, open
                                  source, behavioural examples. Read at Step 4
  input/projects.md               the shared project record: what was built, the
                                  skills each project used, and every metric
  input/quiz-{slug}.txt           optional. Read in Step 10 only, only if the user says yes
  scripts/absorb_skills.py        merges this run's absorbed skills into
                                  input/skill-map.json. Run at Step 8, after delivery
  scripts/resume_date.py          the letter date (resume location's timezone) and
                                  the folder date (OS local time). Run at Step 1.
                                  Its answer is the only date this run may use, for
                                  the folder and the letter alike

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
   go together at Step 2; `input/master-resume.md`, `input/profile.md` and
   `input/projects.md` go together at Step 4. Never read a file twice in a run; hold what you read.
2. **Three shell commands per run.** `python scripts/resume_date.py --json` at Step 1,
   `python scripts/verify_resume.py` at Step 6, and `python scripts/absorb_skills.py` at
   Step 8. Everything else is Read, Glob, Grep or Write. Never `ls`, `cat`, `head` or `mkdir`. The Write tool creates parent directories
   on its own.
3. **Do not narrate.** No phase announcements, no "now analysing the job description", no
   intermediate summaries of the JD or the master resume, no printed plan. Work silently
   from Step 1 to Step 7, then print the report. The analysis in Steps 2 and 3 stays in
   your head; it is never written to chat or to a file.
4. **Write all three output files in one message.** The resume, the cover letter and
   `jd.md` are three Write calls issued together, not three rounds. The JD text is
   already in hand from Step 2, so archiving it costs no read.
5. **Write against the CHECKLIST the first time.** Every gate failure costs a full
   read-fix-verify cycle. Check the list before the Write, not after the failure.
6. **All bookkeeping happens after delivery.** Gap logging and the skill-map merge are
   Step 8, after the user already has the files. They never gate the deliverable. This is
   bookkeeping only: the skills this posting names were already tiered at Step 5 and are
   already on the page. Step 8 records them for the next run, it does not decide them.
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
      that file writes it. No invented, renamed or merged label. An absorbed value goes
      under the nearest of those nine, never under a tenth label
- [ ] 6 to 9 skill categories, and no value repeated across two rows
- [ ] **Every required hard skill the posting names appears literally at least once**,
      in a Technical Skills row if nothing evidences it, unless the exclusion list at
      Step 5 holds it out. A required technology missing from the page is a gate failure,
      not a gap to report
- [ ] No absorbed or `rules.unevidenced` value appears in a bullet, a Key Projects line,
      a Tech Stacks line, the summary or the cover letter. The claim-boundary gate checks
      this one mechanically, so a slip here costs a full fix-verify cycle
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

The two values come from different clocks, on purpose. `letter` comes from the timezone
of the **resume location** recorded in `input/profile.md` section 4, not from the
machine's clock and not from the session date you were told at the start — those two
disagree whenever the machine sits in another timezone than the candidate, and a letter
dated a day ahead of the candidate's own calendar is a tell. `folder` comes from the
machine's own local clock (the OS's `date`), since it is a filesystem detail nobody
reads as a claim about the candidate's calendar, and should sort alongside whatever else
the machine writes that day. Never substitute your own idea of today for either value,
even when it looks right, and never reformat what the script returns.

If the script exits non-zero it says what `input/profile.md` is missing, usually a
`- **Timezone:** <IANA name>` line for a state that spans two zones. **Stop** and report
that, the same as a missing JD.

## Step 2: Job description analysis

**Read `input/jd-{slug}.txt`, `input/track-map.json` and `input/skill-map.json` together,
in one batch.** The caveats are needed at Step 3 and the skill map at Step 5, so reading
both here costs no extra round trip.

Hold the following, without writing any of it to chat:

- Company name. If genuinely absent, infer from domain or email clues, else use "the
  target company" and flag it in the report.
- **Job title, exactly as written.** This becomes `target-role` and drives the headline gate.
- Level, years required, must-have and nice-to-have skills as exact keywords, key
  technologies, certifications, domain expertise.
- **The JD skill inventory, as literal strings.** Every nameable hard skill the posting
  uses: language, framework, library, database, platform, cloud service, protocol,
  standard, regulation, named methodology, tool. Keep the posting's own spelling and its
  acronym form when it gives one (`Spring Boot`, `Kubernetes (K8s)`, `.NET Core`), and
  mark each **Required** or **Preferred** from the way the posting frames it. Do not
  filter this list against the record here. Every entry on it gets a home at Step 5, and
  filtering it this early is what used to drop a must-have off the page before anything
  had looked for one.
- The top 15 to 20 ATS keywords, ranked by importance and frequency. Note variants
  ("Kubernetes" / "K8s") so one mention covers both.
- **Soft requirements, as the exact strings the posting uses**: "excellent written and
  verbal communication", "strong analytical thinking", "attention to detail", "eagerness to
  learn", "collaborate with business analysts and stakeholders". These score as their own
  keyword category and land almost entirely in the summary, so capture the literal wording
  rather than a paraphrase. `input/soft-skills.md` holds what may be claimed against them.
- **Role responsibilities**: what the hire would actually spend time doing, as verbs plus
  objects. Take these from the responsibilities and day-to-day sections, not the skills
  list. Step 5 shapes the document around these, so they matter more than the keyword list.

## Step 3: Caveat check

There is **one master resume**, `input/master-resume.md`: the skills list in Section 1,
then certificates, open source and behavioural examples. There is no track selection, no
primary and no secondary, and nothing in this run chooses between source files. The hard
facts are **not** in that file. They are single-source in `input/profile.md`, with the
project record in `input/projects.md`.

`input/master-resume-bone.md` is the anonymised sharing template. Never read it.

**`input/track-map.json`, read at Step 2, is now a caveat list and nothing else.** Its
`tracks`, `titles`, `keywords`, `default_secondary`, `domain_boost` and `examples` fields
are vestigial; ignore them. What this step uses is every `caveats` entry inside `tracks`,
every `global_caveats` entry, and `no_fit.keywords`:

1. **Caveats.** A caveat fires when any of its `when` strings appears in the JD, or when it
   carries `"always": true`. Every caveat is `action: select_anyway`, which now means the
   run proceeds unchanged: keep the named thing out of the resume, and write its `log` text
   to the gaps file at Step 8. A caveat never blocks and never asks.
2. **`no_fit`.** If any `no_fit.keywords` entry appears in the title or must-haves, the
   posting is outside what the record covers. **Still generate**, from the same master
   resume, and log `no_fit.log` as a structural mismatch at Step 8. There is no fallback
   file to swap in, because there is only one file.

**Matching is on word boundaries, never bare substring.** `erp` must not match inside
"enterprise", and `ai` must not match inside "maintain". Multi-word entries match as phrases.

A caveat is the record telling you what it cannot stand behind, so prefer it over your own
reading of the JD. If a caveat and the posting's responsibilities genuinely disagree,
follow the caveat and log the disagreement at Step 8.

The Technical Skills section comes from `input/skill-map.json` alone, and its ordering is
settled by JD relevance: a category's `track_affinity` list is only a tie-breaker of last
resort, used after JD relevance and before the file's own order.

## Step 4: Read the sources

**One parallel batch of Read calls: `input/master-resume.md`, `input/profile.md`,
`input/projects.md`, `input/soft-skills.md` and `input/keywords.md`.**
Nothing else is read this run.

| Content | Comes from |
|---|---|
| Every fact: employers, titles, dates, locations, education, contacts | **`input/profile.md`**, the only source |
| Projects, what was built, and every metric | **`input/projects.md`**, the only source |
| Technical Skills rows | **`input/skill-map.json`**, the only source for labels and values |
| Soft-skill and competency wording for the summary | **`input/soft-skills.md`**, the only source |
| Practice and domain wording for bullets | **`input/keywords.md`**, bullets only, never a Technical Skills row |
| Certificates and open source, Sections 2 and 3 | **`input/master-resume.md`** |
| Behavioural examples, Section 4 | **`input/master-resume.md`.** Select the closest genuine example to what this posting emphasises; never invent one to fit |

Every file above is single-source: each kind of content exists in exactly one place, so two
files cannot disagree about it. That is why the old cross-track drift rules are gone.

Each project entry carries a `Tracks` line, a `Skills used` line and a `Measured results`
line.

**`input/skill-map.json` is an inventory, not a shortlist, and not a ceiling either.** It
lists what the record already carries, grouped under nine fixed labels, and it is both
longer than any resume can hold and shorter than some postings ask for. So it cuts both
ways. **Select by JD relevance alone**, inside the nine-row budget: a value matching nothing
in this posting does not go on the page however impressive it is, which is how an SAP
architect resume ended up listing Rust, Scala, Dart and SAS; and a skill this posting
requires that the map does not list is absorbed rather than dropped, which is how a Java
posting used to ship a resume with no "Java" on it. Section 1 of the master resume stays
readable as background, but it no longer sets the labels or the values.

**`Skills used` is the evidence line, and it decides placement, not presence.** A skill a
project lists can be claimed at project level: written into a bullet, tied to what was
built. A skill absent from every `Skills used` line has no project behind it, so it belongs
in a Technical Skills row and nowhere else, whether the map already carries it or this
posting brought it in. Never write a bullet around one. The map's caveats and
the library's "Recorded scope limits" both exist to catch this.

A project entry may also carry a **`Recorded gaps`** line. That names detail the project
genuinely lacks, usually specific tooling. Claim what the entry evidences and never what a
gaps line says is unrecorded: naming a vector store or a model the record does not confirm
is fabrication even when the project itself is real.

Rank projects by how well their `Skills used` line matches this posting, then by the
`Tracks` line as a weak hint about the kind of role each project reads for. The tag orders
the work, it never gates it: any project may supply a bullet when its `Skills used` matches
the JD.

Score each role for relevance to the target (90-100 high, 60-89 medium, 0-59 low), and
note as you go the JD requirements nothing in the sources supports. That running list
feeds the report at Step 7 and the gaps log at Step 8. It never reaches the resume.

## Step 5: Generate

Write the resume and cover letter, then issue those two Writes together with the
`jd.md` archive described in Step 7, in a single message.

**Gaps resolve autonomously.** No shortfall stops the run.

| Shortfall | Resolution |
|---|---|
| Missing skill with no trace in the record | **Absorb it into a Technical Skills row** as the posting's literal string, and claim it nowhere else. See *Skill tiering* below. Bridge to a closely adjacent recorded skill in the bullets where one exists (record has FastAPI, JD wants Spring Boot) |
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


**Skill tiering.** Every entry on the Step 2 JD skill inventory falls into exactly one of
four tiers, and the tier decides **where on the page** the skill may appear, never whether
it appears. Settle this before writing a line of the Technical Skills section.

| Tier | Test | May appear in |
|---|---|---|
| **Evidenced** | on a `Skills used` line in `input/projects.md` | anywhere: bullets, Key Projects, Tech Stacks, Technical Skills, summary, cover letter |
| **Inventory** | a value in `input/skill-map.json` that no `Skills used` line carries, including every `rules.unevidenced` value | a Technical Skills row, and nowhere else |
| **Absorbed** | named by this posting, absent from `input/skill-map.json` and from every `Skills used` line | a Technical Skills row under the nearest of the nine labels, and nowhere else |
| **Excluded** | on the exclusion list below | nowhere on the page. Reported at Step 7, logged at Step 8 |

**Absorbed is the tier this skill used to be missing,** and it is the whole reason the
Technical Skills section exists as a listing rather than a claim. A required technology the
record could not evidence used to be logged to `data/{slug}/new-skills.md` after delivery
and left off the page entirely: a Java posting shipped a resume in which the string "Java"
never occurred, which an ATS keyword filter rejects before a human reads a line of it.
Absorbing it puts the posting's own string in the section a screener reads as *what this
person works with*, while every statement of having **used** it stays off the document.

Absorption rules:

1. **Nearest of the nine labels.** Same judgment `scripts/merge_gap_skills.py` encodes:
   a language goes under `Programming Languages`, a cloud service under `Cloud & DevOps`,
   a compliance regime under `Methodologies`, a domain or an architectural pattern under
   `Architecture & Design`. The label set stays closed. Never open a tenth label, and
   never rename one to hold an absorbed value.
2. **The posting's spelling, and its acronym.** Scanners match strings: write
   `Spring Boot`, `Kubernetes (K8s)`, `.NET Core`, `Azure Data Factory (ADF)` the way the
   posting writes them. Where `input/skill-map.json` already carries the value under a
   different wording it is not absorbed at all; it is an inventory value, and the map's
   spelling wins so the page reads consistently.
3. **Listed, never claimed.** An absorbed value may not appear in an achievement bullet, a
   Key Projects line, a `**Tech Stacks**:` line, the summary or the cover letter. Those
   five places each tie a skill to a named employer, project, outcome or first-person
   sentence. A Technical Skills row ties it to nothing, which is what makes listing it
   honest. This is the same boundary `evidence_still_applies` already draws around
   inventory values, and the claim-boundary gate at Step 6 enforces it: it fails the build
   on any `rules.unevidenced` value found outside a Technical Skills row.
4. **Only what this posting names.** Absorption is never padding. A value the posting does
   not use has no business on the page, and adding one is fabrication with extra steps.
   Nothing is absorbed from another run, from `data/{slug}/new-skills.md`, or from your own
   sense of what a role like this usually wants.
5. **Disclosed and recorded.** Every absorbed value is listed in the Step 7 report under
   *Listed but not evidenced*, so the candidate knows exactly what they are being asked to
   speak to in a screen, and merged into `input/skill-map.json` at Step 8 so the next run
   treats it as an inventory value.

**The exclusion list. Never absorbed, however hard the posting pushes:**

- Certifications, licences, clearances and accreditations. Those are credentials, and the
  missing-certification rule stands: omit the entry entirely.
- Degrees, fields of study, institutions.
- Years of experience, seniority, and every `N+ years of X` phrasing.
- Spoken languages, work authorisation, location, relocation, travel, on-site expectations.
- Employer names, customer names, product names of the hiring company, and job titles.
- Soft requirements and competencies. They land in the summary from `input/soft-skills.md`,
  which is their own scoring category. A competency phrase in a Technical Skills row reads
  as a keyword dump and costs more than the match is worth.
- Anything true of a person rather than of a toolkit: "on-call rotation", "mentored
  juniors", "ran the incident review". Those need a bullet, and a bullet needs evidence.

An excluded miss is a real gap. It is reported at Step 7 and logged at Step 8 exactly as
before, and the way to close it is the candidate editing the record, not a row.

**Technical Skills.** Built from `input/skill-map.json`, read at Step 2, plus this run's
absorbed values. Format `- **Category Label**: value, value, value`. The renderer draws
each row as one line of text, label and values together, so a scanner reads the row as the
same single string the markdown carries.

The nine labels in that file are a **closed set**. Write them verbatim, ampersand and
capitalisation included. Never invent a label, never rename one to echo the posting's
wording, never merge two into one, and never split one in two. The point is that the
section reads the same way on every application instead of inventing a fresh taxonomy per
posting, which is the single clearest tell that a machine wrote the page.

Rendering it is five decisions, in this order:

1. **Coverage first.** Before anything is cut, place every Required and Preferred entry
   from the Step 2 inventory that is not on the exclusion list: evidenced and inventory
   values under the label the map gives them, absorbed values under the nearest of the
   nine. **These placements are not negotiable against any budget below.** Everything a
   posting does not name is background, and background is what the budgets cut.
2. **Which rows.** A category holding a value this posting names is rendered. A category
   holding none of them is not, whatever it would do for the row count: an empty or padded
   row is worse than a missing one. Six to nine rows; nine only when the posting genuinely
   reaches all nine labels, which is rare. If a tenth were needed, the label set is still
   closed, so the value goes under the nearest rendered label instead.
3. **Row order.** Most JD-relevant first. Break remaining ties with `track_affinity`,
   preferring the category whose affinity best matches this posting's kind of work, then
   with the order the file lists them in.
4. **Which values.** JD-named values first, in the posting's order of emphasis, then
   background values by JD relevance to fill the row out. 8 to 16 values, or up to 20 where
   the posting itself names that many; a row padded past what the posting asks for reads as
   a keyword dump, and an absorbed value nothing asked for is worse than padding. When the
   1050-word budget binds, cut in this order: background values, then the weakest bullet in
   the least relevant role, then optional sections. **Never buy words by dropping a
   JD-named value.**
5. **Check for repeats.** The file already places each value in exactly one category, so
   rendering it as written cannot repeat a value. An absorbed value is placed once, under
   one label, and the same rule then holds for it. Never restore a repeat by copying a
   value into a second row because the posting uses that wording. A resume naming Docker
   under both Cloud & DevOps and Tools & Platforms has failed this step.

Where a category carries a `recorded_gaps` line, it **limits placement, not listing**, and
the rule the old `Methodologies` gap already stated now governs all of them: a value the
gap names may be rendered in the Technical Skills row when this posting names it, and no
bullet, Key Projects line, Tech Stacks line, summary sentence or letter may claim it was
practised, facilitated or shipped. So `Agile / Scrum` and the ceremony names list without
a bullet behind them, a vector store or model provider the posting asks for by name lists
under `Data & AI` and appears in no achievement, and `Cypress` or `Playwright` lists under
`Testing` and is tied to no project. What a gap still forbids absolutely is inventing a
value nobody asked for to close it, and any AI or testing **metric** the record does not
carry. Log any gap that cost real JD coverage at Step 8.

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
thing. Select by which `Skills used` lines match the posting, then by the `Tracks` line.
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

Six blocking gates: human style, frozen facts, headline, emphasis budget, structure and
length, and **claim boundary**. The last one reads `rules.unevidenced` from
`input/skill-map.json` and fails the build if any of those values appears outside a
Technical Skills row: in a bullet, a Key Projects line, a Tech Stacks line, the summary or
the letter. That is the listed-never-claimed rule, machine-checked, which is what lets the
page carry the posting's whole keyword set. The header block is exempt, because the
headline is the target job title and a posting called "Kubernetes Engineer" claims nothing.
`convert_resume.py` runs the same gates plus a page-count check and writes no PDF if any
fails.

A claim-boundary failure is fixed by **rewording the sentence, never by deleting the row**:
the keyword stays on the page where it belongs, and the claim around it goes.

Fix the markdown until they pass. **Never reach for `--no-verify`**; that flag is for
inspecting a work-in-progress layout, not for shipping. If a gate fails, fix only what it
names and re-run once. Do not re-read the master resume to fix a style gate.

Then read once more for what the gates cannot see: most relevant experience first, and
no sentence that sounds like a press release. Facts need no cross-checking any more:
`input/profile.md` is their only source, and the gate reads it.

**Coverage sweep.** The gates count words and rows; they cannot tell whether this posting's
language reached the page. ATS scoring splits into three categories, so sweep all three,
once, before delivering. Take the lists captured at Step 2.

| Category | Check | Where it should land |
|---|---|---|
| **Hard** | **Every Required technology appears as the posting's literal string, and every Preferred one the exclusion list does not hold out.** Target: all of them | A bullet where `Skills used` allows one, a Technical Skills row otherwise |
| **Soft** | Up to three of the posting's competency phrases appear | Summary, attached to something concrete |
| **Industry** | The sector, or the nearest honest adjacency, and the posting's process vocabulary appear | Summary and bullets |

**Hard coverage is the one sweep line that blocks.** Search the draft for each Required
string. A miss has exactly three legitimate resolutions, and "report it and ship" is no
longer one of them:

| Why it is missing | Resolution |
|---|---|
| Nothing evidences it, and it was never absorbed | Absorb it now, into the nearest rendered row, and re-run the gates |
| It is on the exclusion list | Correct. Leave it off and report it at Step 7 as an unmet requirement |
| It is there under the map's wording, not the posting's | Add the posting's string to the row where the two spellings differ enough to miss (`Postgres` / `PostgreSQL` is one string to a scanner, `Spring Boot` / `FastAPI` is not) |

Two placement failures to look for after that:

- **A buried must-have.** A required keyword sitting only in the Technical Skills row is
  matched but weakly placed. If `input/projects.md` carries it on a `Skills used` line, work
  it into the bullet for that project. If it does not, the row is the right and only home
  for it: that is the tiering rule, not a defect.
- **A silent category.** A summary with no competency phrase scores near zero on Soft
  however strong the bullets are, because Soft has nowhere else to land.

**One revision pass, then stop.** Fix what the sweep names, re-run the gates once, and
deliver. The pass may place a JD-named string into a row and re-word or re-place material
the record supports. It may never move an absorbed or inventory value into a bullet, a
Tech Stacks line, the summary or the letter to improve its placement score, and it may
never narrow the keyword list until the number looks better. If a second pass looks
necessary, the gap is in the record, not the wording, and it belongs in
`data/{slug}/master-resume-gaps.md`.

## Step 7: Deliver

All three files go to `output/{YYYYMMDD}/{company}-{position}/`, each path component
lowercased with non-alphanumeric runs collapsed to hyphens. `{YYYYMMDD}` is the `folder`
value from Step 1, the machine's own local date — it can differ from the letter's date
when the candidate's timezone and the machine's disagree near midnight; that is expected,
not a bug to reconcile. The Write tool creates the folder.

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
**Caveats fired**: [each caveat this posting triggered, or "none"]

### Coverage
- Must-have keywords covered: [X/Y]  ([N] evidenced in bullets, [N] listed in rows only)
- Nice-to-have keywords covered: [X/Y]
- Skills absorbed this run: [N, or none]
- Resume length: [N] words

### Listed but not evidenced
- [absorbed or inventory value] - [the row it went in]. Listed for the scanner, claimed
  in no bullet and in no letter. Be ready to say honestly how much of it you have, or
  strike it before sending

### Not claimed
- [keyword] - [why it could not go on the page at all: exclusion-list class, or a
  credential, and what would close it]

### Omitted for missing detail
- [e.g. SAP certification: recorded as held, but no name, module, date or ID. Add those
  to Section 2 of input/master-resume.md to include it next run.]
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
`data/{slug}/new-skills.md` and `data/{slug}/master-resume-gaps.md`, and fold this run's
absorbed values into the skill map.

**This is one Grep call, at most two Writes, and one shell command.** Read `logging.md`
for the entry formats and the classification rules. Nothing here changes the files written
at Step 7.

**Merge the absorbed values into `input/skill-map.json`:**

```
python scripts/absorb_skills.py --slug {slug} "Programming Languages=Java,Kotlin" "Frameworks & Libraries=Spring Boot"
```

One `Label=value,value` argument per label, using the label spellings the map already
uses and the same placements the page rendered. The script is idempotent, adds each value
to that category and to `rules.unevidenced`, skips anything already present under any
label, and prints what it changed. `--dry-run` shows the plan without writing.

That is the loop this skill used to leave open: the next posting that names Java finds it
in the map as an inventory value, so it renders without being absorbed again, and it stays
barred from bullets by `evidence_still_applies` until a real project carries it on a
`Skills used` line. Pass only what this run actually rendered. Never feed the script a
value the resume did not carry, and never feed it an exclusion-list item.

**When the same gap keeps being logged, the fix is the record, not the next run.** A value
listed on every resume and evidenced by none, or a project still reading
`Measured results: None recorded`, is what the `resume-project-deepener` skill exists for:
it works the gaps logs into questions for the candidate and writes their answers into
`input/projects.md`, after which `scripts/promote_skills.py` lifts the claim bar on
anything the project record now carries. Never do that work inside this run, and never
write to `input/projects.md` from this skill.

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
  way to act on it is a fresh run against a revised master resume, not a patch to this output
- Hard coverage was already checked and closed at Step 6, so a low Hard number here means
  the checker read a string the posting uses that Step 2 did not capture. That is worth a
  line in the gaps log for the next run, not an edit to this one

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
metrics. **Never claim a JD-only skill:** a skill the record cannot evidence may be listed
in a Technical Skills row, which asserts nothing about where it was used, and it may never
appear in a bullet, a Key Projects line, a Tech Stacks line, the summary or the cover
letter, which all do. Listing is not claiming, and that distinction is what lets the page
carry the posting's full keyword set without a sentence on it being untrue. Everything
else is reorder, reframe and select from existing content.

**Never block.** Produce both deliverables on every run. The sole exception is a missing
job description, which is a missing input rather than an uncertainty. Uncertainty goes to
the gaps log at Step 8, not to a prompt.

**Authenticity.** Do not distort an achievement to fit the JD, and do not oversell impact.
What the candidate cannot defend in a technical screen does not go on the page.

**Honesty about gaps.** Full keyword coverage is the target, and disclosure is what keeps
it honest. Every value the page lists without evidence behind it is named in the Step 7
report under *Listed but not evidenced*, so the candidate sees exactly what a screener
will ask them about and can strike any line they would rather not defend. Requirements
that cannot go on the page at all, the exclusion-list classes and the missing credentials,
are reported every run. What is never allowed is a keyword list quietly narrowed until the
number looks better, or an unevidenced skill smuggled into a bullet to place it more
strongly.

Unusual conditions are in `edge-cases.md`. Read it only when one fires.
