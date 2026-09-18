---
name: resume-project-deepener
description: Use when input/projects.md is thinner than the work it records - expands the project library to the full scope of what a senior engineer actually did on each project, by proposing the unrecorded surface layer by layer and writing only what the candidate confirms. Also promotes newly evidenced skills out of rules.unevidenced so bullets may finally claim them.
---

# Resume Project Deepener

## Overview

`input/projects.md` is the evidence file. Every bullet, every metric, every `Tech Stacks`
value and every sentence in a cover letter is allowed onto a resume because a `Skills used`
line here carries it, and the claim-boundary gate fails the build when something claims
more than this file supports.

Which makes a thin record expensive. The four Centene entries and three Blue Stingray
entries describe perhaps a fifth of what seven years of senior engineering actually
involved. Everything in the other four fifths is currently unclaimable: it either sits in a
Technical Skills row as a listed-but-unevidenced value, or it is absent from the page
altogether and logged as a gap after every run.

**This skill closes that gap from the candidate's own answers, and only from those.**

**Core principle: the record is thinner than the work, and the fix is recall, not
invention.** The job is to work out what a senior engineer on this project almost certainly
did, put it to the candidate as a question, and write down the answer. A project entry
expanded from anything other than an answer is fabrication with better grammar, and it
fails in a technical screen rather than on the page.

## When to Use

- The user asks to expand, deepen, enrich or fill out `input/projects.md`.
- A run's report or `data/{slug}/master-resume-gaps.md` shows the same gaps over and over:
  no volume figures, no broker named, no document store, no AI number.
- The user volunteers real experience that has nowhere to live yet.

**DO NOT use for:** writing a resume (that is `resume-jd-optimizer`), scoring one
(`resume-ats-checker`), or editing `input/profile.md` facts. Employers, titles, dates,
locations, education and contacts live there and are corrected there.

---

# THE ONE HARD RULE

**Nothing reaches `input/projects.md` without an explicit confirmation in the
conversation.** Not a plausible inference, not an industry norm, not "a senior engineer
would obviously have done this", not something the candidate said about a different
project.

| What the candidate said | What may be written |
|---|---|
| "Yes, RabbitMQ was the broker" | `RabbitMQ` on that project's `Skills used` line |
| "Yes, about 2 million records a night" | `2 million records a night` in `Measured results`, in their words |
| "I think we had something like that" | **Nothing.** Ask once more for the specific; on a second vague answer, stage it and move on |
| "Skip" or silence | **Nothing.** Staged as unconfirmed, never written |
| Nothing, because the question was never asked | **Nothing** |

Everything proposed and not confirmed goes to `data/proposals/projects-{YYYYMMDD}.md`, which
no other skill reads. That file is a parking space, never a source.

**Never invent a number.** A metric enters `Measured results` only as a figure the candidate
states. "It got much faster" is qualitative and stays qualitative. A range is acceptable
when they give the range ("somewhere between 40 and 60 a day"); a range you inferred is not.

**Never widen an answer.** "We used Kafka for the events" licenses `Kafka` on that project,
not `event-driven architecture` as a claimed practice, not Kafka on the other employer's
projects, and not a bullet about designing the topology.

---

# WORKFLOW

## Step 1: Back up, then read

```
python scripts/resume_date.py --json
```

Copy `input/projects.md` to `input/projects_backup_{folder}.md` before the first write of
the session, where `{folder}` is the script's `folder` value. One backup per session: if the
file already exists, it is this session's and is left alone.

Then read, in one batch:

| File | For |
|---|---|
| `input/projects.md` | the current record, and every `Recorded gaps` line |
| `input/profile.md` | employers, roles and periods, so a new project entry inherits the right ones |
| every `input/master-resume-*.md` except `-bone` | Section 1 skills with no project behind them |
| `input/skill-map.json` | `rules.unevidenced`: everything the resumes have been listing without evidence |
| `data/*/master-resume-gaps.md` | what recent runs said would have made a better resume |
| `data/*/new-skills.md` | which skills postings keep asking for, and how often |

## Step 2: Rank the gaps by what they would actually buy

Do not start at the top of the file. Start where a confirmation converts into the most
resume, and say why when asking. The order:

1. **Listed but unevidenced, and frequently demanded.** A value in `rules.unevidenced` that
   also appears in several `data/*/new-skills.md` entries is being printed on every resume
   with nothing behind it. One confirmation moves it from a row into a bullet, which is the
   single largest change available to this record. Count the appearances; ask about the
   highest counts first.
2. **Projects reading `Measured results: None recorded`.** Screeners look for about five
   quantified outcomes and this record has nine, all from three projects. A number here is
   worth more than any rewording.
3. **`Recorded gaps` lines.** They name exactly what the project lacks, in the project's own
   terms. The AI Knowledge Assistant's missing model provider, vector store and accuracy
   figure is the most expensive single gap in the file.
4. **Itemisation gaps.** A skill in Section 1 of a track file that no project carries. The
   candidate already claims it; it just has no project attached.
5. **Unrecorded projects.** Seven entries across seven years is a fraction of the work. Ask
   what else shipped, per employer, once the existing entries are filled out.

## Step 3: Build the scope inventory

Read `scope-inventory.md`. For each project, derive the unrecorded surface from what the
entry already records, layer by layer: a FastAPI service on PostgreSQL behind an RBAC and
PHI boundary implies migrations, pagination, error taxonomy, connection pooling, secrets
rotation and load testing, whether or not any of them is written down.

**This is the creative step, and its output is questions.** The inventory tells you what a
senior engineer on that project plausibly touched. It never tells you what they did.

## Step 4: Ask, in batches

- **At most 8 questions per batch**, highest value first, grouped by project so the
  candidate stays in one context.
- Each one answerable in a few words: yes or no, a number, a name, or `skip`.
- Say what each answer would unlock, in one clause. "Confirming the broker would let the
  Centene integration bullet name it instead of listing Kafka in a skills row."
- Never ask two things in one question, and never ask for a number and a name together.
- Batch format:

```
Centene, Claims and Provider Data Integration

1. What was the broker behind the Celery queues: Redis only, RabbitMQ, Amazon SQS, something else?
2. Roughly how many records a day moved through those 4 services? A number or a range.
3. Did you write the database migrations for those tables yourself? (yes / no)
4. Was there a dead-letter or replay path for records that failed twice? (yes / no)

Answer any of them, skip the rest.
```

- A `yes` that needs a specific gets one follow-up, then stops. Two vague answers on the
  same item means it is genuinely not recallable: stage it.

## Step 5: Write what was confirmed

Preserve the file's entry contract exactly. An entry is:

```markdown
### Project Name

- **Company:** <from input/profile.md>
- **Period:** <the employing role's period> (role period)
- **Tracks:** <fs, data, devops, enterprise, ai - by subject matter>
- **Skills used:** <comma-separated, the candidate's own names for things>
- **Measured results:** <figures as stated, or "None recorded.">
- **Recorded gaps:** <what is still unrecorded, when anything is>

<prose: what it does, what was built, who used it>
```

Rules for each part:

- **`Skills used`** grows by appending confirmed items. Keep the existing order and add to
  the end of the relevant run, so a diff reads as additions.
- **`Measured results`** takes the figure in the candidate's words, with the unit and the
  baseline where they gave one. Never round, never annualise, never convert.
- **Prose** grows by at most two sentences per confirmation round, and describes what was
  built rather than how impressive it was.
- **`Recorded gaps`** shrinks: delete the clause a confirmation closed. If a gaps line ends
  up empty, remove the line. If a confirmation opens a new gap ("we used a vector store but
  I cannot remember which"), write that clause in.
- **A new project entry** inherits `Company` and `Period` from `input/profile.md`. Never
  invent a period, never write a project-specific date range, and never attribute a project
  to a company the profile does not list.
- **Never touch** `Company`, `Period` or the `## Employer` headings on an existing entry
  without an explicit correction from the candidate, and never edit
  `input/master-resume-bone.md`.

Write the whole file once, at the end of the batch, not per answer.

## Step 6: Promote what is now evidenced

A skill with a project behind it is no longer unevidenced, and leaving it in
`rules.unevidenced` keeps the claim-boundary gate blocking the bullet the candidate just
earned.

```
python scripts/promote_skills.py
```

The script reads `input/projects.md` itself and removes from `rules.unevidenced` only the
values it can find on a `Skills used` line there, so it cannot promote anything on the
strength of this conversation alone. It prints what it promoted and what it left. Pass
`--dry-run` to see the plan.

Then tell the user which Section 1 heading of which `input/master-resume-*.md` each promoted
skill belongs under, and offer to add it. That edit is one line per track file and it is
what makes the skill selectable on the next run.

## Step 7: Report

```
## PROJECT RECORD UPDATED

**Backup**: input/projects_backup_{folder}.md

### Added
- [project] - [what was added: skills, metric, prose, or a whole entry]

### Promoted out of rules.unevidenced
- [value] - now claimable in a bullet, because [project] carries it

### Still unconfirmed
- [item] - staged in data/proposals/projects-{folder}.md

### What this changes on the next run
- [e.g. "asynchronous message queues can now be claimed in the Centene bullet by name,
  where the Motion run had to list Kafka and RabbitMQ in a skills row"]
```

Name the postings it would have changed where the gaps logs make that clear. That is the
feedback loop the logs exist for.

---

# CORE CONSTRAINTS

**Confirmation is the only source.** Every other input to this skill - the scope inventory,
the gaps logs, the unevidenced list, the postings - decides what to *ask*. None of them
decides what to write.

**No metric without a figure from the candidate.** This is the rule most worth holding: a
number is the most load-bearing thing on a resume and the easiest to challenge.

**No technology the candidate did not name.** Not the one that would have scored best, not
the one the posting asked for, not the obvious default for that stack.

**Facts stay where they live.** Employers, titles, dates, locations, education and contacts
are `input/profile.md`. Skills lists, certificates, open source and behavioural examples are
the track files. This skill writes `input/projects.md`, and asks before touching anything
else.

**A thin answer is a real answer.** "I do not remember" keeps the gap honest and keeps it
logged. That is a better outcome than a filled-in field nobody can defend.
