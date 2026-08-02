# Resume-JD Optimizer

Turns a job description plus the candidate's master resume into a tailored,
two-page resume and a matching cover letter, both of which read as if a person
wrote them.

```
Input:
  - input/jd-{worktree}.txt         job description, one per worktree
  - input/master-resume.md          the source of truth for every FACT
  - input/master-resume-{track}.md  per-track skill sources, selected in Phase 1.2

Output:
  - output/{YYYYMMDD}/{company}-{position}-{name}.md
  - output/{YYYYMMDD}/{company}-{position}-{name}-cover.md
  - data/new-skills-{worktree}.md            appended, never asked about
  - data/master-resume-gaps-{worktree}.md    appended, never asked about
```

The markdown is then rendered by `scripts/convert_resume.py`, which refuses to
write a PDF unless the file passes every gate in `scripts/verify_resume.py`.
**Those gates are the real specification.** Everything below exists to produce a
file that passes them on the first try. Read the OUTPUT CONTRACT section before
writing a single line of output.

## The run does not stop to ask

The resume and cover letter are always produced. There is no confirmation step,
no "should I proceed anyway", no multi-select skill check. When the master
resumes cannot support something the JD wants, the skill makes the best honest
call it can, ships the deliverable, and **writes the problem to a file in
`data/` for the candidate to review later.** Two files carry everything that
would previously have been a question:

| File | Holds |
|---|---|
| `data/new-skills-{worktree}.md` | JD skills with no match in any master resume |
| `data/master-resume-gaps-{worktree}.md` | anything that made this run harder or weaker than it should have been |

The only interactive point left is the Phase 8 follow-up loop, which happens
**after** both files are written and never blocks the deliverable.

---

# HOUSE STYLE

This is the part that has historically gone wrong, so it comes first.

## Write like a person, not like a model

- **No em dashes, en dashes, arrows, ellipsis characters, curly quotes, or
  bullet glyphs.** Use a comma, a colon, a full stop, or a new sentence. Gate 1
  blocks the build on any of them, and they are the single loudest tell that a
  machine wrote the document.
- **No AI register.** Banned outright: leverage, delve, seamless, robust and
  scalable, spearhead, cutting-edge, showcase, underscore, pivotal, meticulous,
  synergy, testament to, state-of-the-art, at the forefront, furthermore,
  moreover, not only. Say the plain thing instead.
- **No square brackets anywhere in the output.** Not for placeholders, not for
  `[AI-Generated]` markers, not for `[to be supplied by candidate]`. If a fact is
  not available, the entry is omitted from the resume and reported in chat.
- Short declarative sentences. One idea per bullet. A number where a real number
  exists, and plain language where one does not.

## No inline bold

Bold is used in exactly one place: the label of a technical-skill row.

Bolding keywords buys nothing at the ATS layer, which reads the plain text
either way, and 250 bold runs on a page cancel each other out as emphasis. The
document is scanned by a human in about 40 seconds; structure does that work,
not typographic shouting. There is no keyword-emphasis pass in this skill.

## Two pages, hard

Budget is roughly 900 words and never above 1050. Anything that does not earn
its place against this specific job description comes out. A resume that runs to
five pages is not read.

---

# OUTPUT CONTRACT

The markdown is parsed structurally, so it is not free-form. Emit exactly this
shape:

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

Rules the renderer depends on:

| Element | Form | Renders as |
|---|---|---|
| Metadata | `<!-- key: value -->` at the top | stripped from the PDF; drives the headline gate |
| Name | `# Name` | centred, bold |
| Headline | the line directly under the name | centred italic, one line |
| Contact | the lines after that, until a blank | centred, one or two lines |
| Section | `## Title` | uppercase heading with a rule under it |
| Entry | `### Title \| dates \| location` | title bold left, dates and location grey right, same line |
| Entry subtitle | `#### Company` on the next line | italic grey under the title |
| Skill row | `- **Label**: values` | two-column label and value |
| Bullet | `- text` | hanging indent, full width |
| Prose | a plain line | body paragraph |

- Dates are always `MM/YYYY - MM/YYYY`. The gate matches them against the master
  resume, which writes them as month names, so any real date will verify.
- Write URLs bare, as `linkedin.com/in/handle`, not as markdown links. The
  renderer turns bare URLs and email addresses into clickable links while
  leaving the visible text exactly as written, which is what an ATS reads.
  Square brackets are banned, so `[LinkedIn](url)` fails the gate anyway.
- Blank lines and `---` are ignored by the renderer. Spacing is structural. Do
  not try to control layout from the markdown.
- No markdown tables. No emoji. No HTML beyond the metadata comment.
- Required sections: Summary, Technical Skills, Professional Experience,
  Education. Optional: Certifications, Languages.
- Forbidden sections: Core Competencies, Key Skills, Core Skills, Leadership &
  Impact, Gap Analysis. The first three duplicate Technical Skills; the fourth
  restates the experience bullets; the fifth belongs in chat.

The cover letter uses the same header block plus `kind: cover`, then date,
recipient, salutation, body paragraphs and sign-off as plain prose. No sections,
no bullets, 250 to 400 words.

---

# PHASE 0: RUN CONTEXT

Several sessions can run against this repo at once, each in its own worktree and
each working a different posting. So the job description this skill reads, and
every file it writes outside `output/`, is namespaced by worktree.

## Resolve the worktree slug, once, at the start of the run

```
git rev-parse --show-toplevel
```

Take the final path segment, lowercase it, and replace every run of
non-alphanumeric characters with a single hyphen. That is `{worktree}`. A
checkout at `f:\Work\Tech\resume-generator-v2-gafari` gives
`resume-generator-v2-gafari`.

If the command fails (not a git repo), use `local` and note it in the Phase 7
report.

## Locate the job description

The JD is **`input/jd-{worktree}.txt`**. Resolve it before Phase 1:

1. `input/jd-{worktree}.txt` exists: use it. This is the normal case.
2. It does not exist, but `input/jd.txt` does: use `input/jd.txt`, and say so in
   the first line of the Phase 7 report. This is the single-session fallback and
   is **unsafe when sessions run concurrently**, because every worktree without
   its own file will read the same posting and overwrite each other's reasoning.
   Name the file the worktree expects, so the candidate can create it next time.
3. Neither exists: **stop.** Report which paths were checked and what to create.
   This is a missing input, not an uncertainty to work around, and generating a
   resume without a posting is not possible. It is the one condition that halts a
   run.

Never read a `jd-*.txt` belonging to another worktree, even when the expected one
is missing. That is another session's posting, and it is probably mid-run.

## Writing to the data files

- `mkdir -p data` first. The directory may not exist on a fresh clone.
- **Append. Never rewrite, never reorder, never delete an earlier run's
  entries.** These files are the candidate's weekend review queue.
- Read the file before appending, so a skill already recorded for the same track
  is not logged twice. If it is already there, add the new JD to its
  `Seen in:` line instead of creating a second entry.
- Every append opens with a run header so entries can be traced back:

```markdown
## 2026-08-02 | Accuris | SAP Solution Architect
```

- Under that header, group entries by track, using the track's display name as a
  `### ` heading. A run that touches two tracks writes two groups.
- If a run has nothing to add to a file, do not touch that file and do not write
  an empty run header.

---

# PHASE 1: JOB DESCRIPTION ANALYSIS

Parse the job description resolved in Phase 0 and structure:

- Company name. If genuinely absent, infer from domain or email clues, otherwise
  use "the target company" and flag it in the Phase 7 report. Do not stop to ask.
- **Job title, exactly as written.** This becomes `target-role` in the metadata
  and drives the headline gate, so copy it verbatim.
- Position level, primary role, secondary role, years of experience required
- Must-have skills and nice-to-have skills, as exact keywords
- Key technologies, required certifications, domain expertise, soft skills
- The top 15 to 20 keywords for ATS purposes, ranked by importance and frequency

Note keyword variants ("Kubernetes" / "K8s") so a single mention covers both.

Then extract the **role responsibilities**: what the person hired into this job
would actually spend their time doing, stated as verbs plus objects ("build and
operate Kubernetes clusters", "author API reference documentation"). Take these
from the JD's responsibilities and day-to-day sections, not from its skills list.
Phase 1.2 selects source files from these, so they matter more than the keyword
list.

---

# PHASE 1.2: TRACK SELECTION

`input/master-resume.md` is large and covers every direction the candidate could
apply in. Reading all of it for a single JD buries the relevant material. The
per-track files exist for this: each is the same record filtered to one kind of
role.

## Pick tracks from responsibilities, not from the job title

A title can be marketing. Responsibilities are what the work is. Match the
responsibilities extracted in Phase 1 against this table and select **every**
track that covers a meaningful part of the job.

| Track file | Select when the work involves |
|---|---|
| `master-resume-fs.md` | web application delivery, frontend, backend, APIs, general software engineering |
| `master-resume-data.md` | pipelines, warehousing, ETL/ELT, analytics engineering, BI, statistical programming |
| `master-resume-devops.md` | cloud infrastructure, Kubernetes, IaC, CI/CD, SRE, platform engineering, observability |
| `master-resume-security.md` | application or cloud security, SOC, incident response, GRC, compliance, pentesting |
| `master-resume-enterprise.md` | SAP, Salesforce, ServiceNow, Workday, ERP/CRM/ITSM configuration and integration |
| `master-resume-it-operation.md` | endpoint and device management, service desk, sysadmin, networking, IT operations |
| `master-resume-mobile.md` | iOS or Android application work, cross-platform mobile |
| `master-resume-ai.md` | LLM and generative AI, RAG, ML engineering, MLOps, applied data science |
| `master-resume-product.md` | product ownership, roadmap, discovery, experimentation, technical program management |
| `master-resume-writer.md` | documentation, API references, knowledge bases, docs-as-code |
| `master-resume-blockchain.md` | **backend or infrastructure work at a web3 company only** |

Rules:

- **Most JDs select one or two tracks. Three is possible for a genuine hybrid.
  Four or more means the matching is too loose: keep the two strongest and log
  the rest as secondary in the Phase 7 report.**
- Rank the selected tracks. The first is primary and drives the headline, the
  summary, and the ordering of the Technical Skills categories. The others
  contribute skills but do not reshape the document.
- `master-resume-blockchain.md` is an integration track. **Never select it for a
  smart-contract, protocol, or security-audit role.** It has no Solidity, no
  chains, no web3 tooling and no crypto domain content, by design. If the JD is
  one of those, select nothing from it, generate from the other tracks, and log
  the mismatch to the gaps file.
- If no track fits (a mechanical, fire protection, process or structural
  engineering posting, for example), fall back to `input/master-resume.md` alone
  and log that the JD is outside every track.

## What each file is authoritative for

| Content | Read from |
|---|---|
| Skills, Sections 1 and 2 | the selected track files |
| Every fact: companies, titles, dates, locations, education, contacts, certifications, Sections 3 to 15 | **`input/master-resume.md`, always** |

This split is not cosmetic. The frozen-facts gate validates the output against
`input/master-resume.md` and nothing else, so a company, date, school or contact
value taken from anywhere else will fail the build.

The track files are filtered views of the master, so their skills are a subset
of it. If you find a skill in a track file that is genuinely absent from
`input/master-resume.md`, the files have drifted: use it, and log the drift to
the gaps file so the master can be corrected.

---

# PHASE 1.5: NEW SKILL DETECTION AND LOGGING

Keyword-spotting against a JD is noisy: it over-triggers on generic words, on
near-duplicates of skills already listed under another name, and on technologies
the JD mentions in passing. Writing any of that into `input/master-resume.md`
would fabricate a claim about the candidate.

**This step used to stop and ask. It does not any more.** Detected skills are
written to `data/new-skills-{worktree}.md` and the run continues. The candidate
reviews that file on their own schedule and decides what, if anything, belongs in
a master resume. Nothing detected here is used in this run's output.

## Step 1: build the list

1. Take the JD's key technologies and must-have / nice-to-have skills.
2. Normalise both those and Section 1 of **every track file selected in Phase
   1.2**, plus Section 1 of `input/master-resume.md`, case-insensitively,
   collapsing well-known aliases (".NET" / ".NET Core" / "dotnet", "JavaScript" /
   "JS", "Postgres" / "PostgreSQL"). An alias is not a new skill.
3. Drop generic non-skill noise: "software", "programming", "experience",
   "team player", "communication skills".
4. Classify each surviving term:
   - **Evidenced elsewhere in the master resume but not itemised in Section 1**:
     an itemisation gap. Usable this run, still worth logging.
   - **In `input/master-resume.md` but missing from the selected track file**: a
     filtering gap. Usable this run. Log it so the track file can be corrected.
   - **Not evidenced anywhere**: a genuinely new claim. **Not usable this run.**
5. Rank must-haves first, then nice-to-haves, ties broken by JD emphasis.

If nothing survives, write nothing and go to Phase 2.

## Step 2: write the entries

Append to `data/new-skills-{worktree}.md` under the run header, grouped by the
track the skill would belong to. Choose the track from the skill's subject
matter, not from which track happened to be selected this run: a Kubernetes skill
is logged under Cloud / DevOps Engineer even on a JD that selected only Full
Stack.

Each entry records where the term came from and what evidence exists, so the
candidate can decide without reopening the JD:

```markdown
## 2026-08-02 | Accuris | SAP Solution Architect

### Enterprise Platform Engineer

- **SAP BTP Integration Suite** - must-have, JD says "3+ years hands-on with BTP
  Integration Suite". Status: not evidenced anywhere in the master resumes.
  Nearest recorded: SAP CPI, SAP PI/PO. Seen in: Accuris SAP Solution Architect.
- **CDS views** - nice-to-have. Status: evidenced in the Section 5 project text
  but not itemised in Section 1. Nearest recorded: ABAP, HANA modelling.
  Seen in: Accuris SAP Solution Architect.

### Cloud / DevOps Engineer

- **Azure DevOps release gates** - nice-to-have. Status: filtering gap, present
  in master-resume.md but absent from master-resume-devops.md.
  Seen in: Accuris SAP Solution Architect.
```

Required per entry: the skill name, whether the JD called it a must-have or a
nice-to-have, its status from Step 1's classification, the nearest thing already
recorded, and the JD it was seen in.

## Step 3: keep it out of this run's output

- A skill logged as **not evidenced anywhere** is a missing skill for Phase 3.
  Bridge to an adjacent recorded skill or omit it. **Never put it in the resume
  on the strength of having logged it.** Logging is a note to the candidate, not
  a confirmation.
- Itemisation gaps and filtering gaps are already true of the candidate, so they
  are usable in the output as normal.
- Do not edit `input/master-resume.md` or any track file to add a detected skill.
  That decision is the candidate's, and they make it against the file, not
  mid-run.

---

# PHASE 2: MASTER RESUME PARSING

From `input/master-resume.md`, extract the facts: name, email, phone, location,
LinkedIn, GitHub, career history (company, title, dates, location, achievements,
technologies), education, certifications, open source, behavioural section.

From **each track file selected in Phase 1.2**, extract Sections 1 and 2. Union
the skills across the selected tracks and drop duplicates. Where two tracks word
the same skill differently, keep the wording from the primary track.

Score each role for relevance to the target position (90-100 high, 60-89 medium,
0-59 low).

## Section 2 core skills are a bias, not a mandate

**Section 2, "Always-Required / Core Skills"** in each selected track file is the
candidate's own standing declaration of how they want to be positioned for that
kind of role. Give those skills preference when choosing what to include, and
keep the candidate's genuine domain visible even on an unrelated posting. When
several tracks are selected, the primary track's Section 2 outranks the others.

But the two-page budget wins. Do not carry every Section 2 entry into every
resume regardless of relevance: that is how an SAP architect resume ended up
listing Rust, Scala, Dart and SAS. Include the ones that fit the eight-category
budget, prefer them over equally irrelevant alternatives, and let the rest go.
Never bold them unless they are also genuine JD keywords.

---

# PHASE 3: GAP ANALYSIS AND MATCHING

Classify every JD requirement as:

1. **Exact match**: prioritise.
2. **Partial match**: bridge with adjacent terminology.
3. **Missing critical skill**: resolve autonomously, below.
4. **Missing metric**: resolve autonomously, below.
5. **Missing certification**: resolve autonomously, below.

## Autonomous gap resolution

**Nothing in this phase stops to ask.** Whatever the shortfall, make the best
honest call available, produce the deliverable, and record the problem in
`data/master-resume-gaps-{worktree}.md`.

- **Missing critical skill with no trace in any master resume**: do not
  fabricate. Omit it. If a closely adjacent skill exists (resume has Kubernetes,
  JD wants Helm), bridge it as a partial match.
- **Missing metric**: never invent a number. Use honest qualitative phrasing, or
  a conservative estimate only where the surrounding master-resume text implies a
  range. Flag any estimate in the report.
- **Missing certification**: **omit it.** See Phase 4.
- **The JD's core requirement is something the candidate simply does not have**:
  still generate. Lead with the strongest genuine overlap, do not inflate, and
  log it as a hard mismatch. A weak honest resume is a usable artifact; a refusal
  to generate is not.

## The gaps log

`data/master-resume-gaps-{worktree}.md` answers one question for the candidate at
the weekend: *what would have made this run produce a better resume?* Append,
grouped by track, under the standard run header. Log any of these:

| Situation | Example entry |
|---|---|
| A must-have with no support anywhere | Kubernetes operators: JD must-have, nothing recorded. Would need a real example to claim. |
| Fewer than five quantified results available | Only 2 real metrics exist for this track. Bullets X and Y would carry numbers if the candidate supplied them. |
| A recorded claim too thin to use | SAP certification recorded as held, but no name, module, date or ID, so the entry was omitted. |
| A track file too thin for the JD it was selected for | master-resume-writer.md has no writing portfolio, so the JD's "please link samples" cannot be answered. |
| Drift between a track file and the master | OpenAPI is in master-resume-writer.md but not in master-resume.md. |
| A structural or positioning problem | JD wants 15+ years systems engineering; record supports ~9y7m software. Cannot be closed by wording. |
| No track matched the JD | Fire protection engineering posting; generated from master-resume.md alone. |
| Anything that forced a judgment call | Two employers plausible for this project; picked the later one on date overlap. |

Write what would fix it, not just what was wrong. "Add the state and licence
number to Section 12" is useful; "PE licence incomplete" on its own is not.

## Track what you deliberately did not claim

Keep a running list of JD keywords the master resumes cannot support. This list
goes in the Phase 7 chat report and the gaps file, never in the resume. It
matters: a resume that scores 100% against a keyword list the candidate cannot
defend in a technical screen is worse than one that scores 80% honestly.

---

# PHASE 4: CERTIFICATION HANDLING

**Never generate a certification.** This skill previously defaulted to inventing
plausible credentials marked `[AI-Generated]`, and those markers shipped inside
delivered PDFs. Credentials are individually verifiable, so a fabricated one is
trivially disproved by any recruiter who checks, and the bracketed marker itself
makes the document unsubmittable.

The rule now:

1. **Certification present and complete in the master resume**: include it, as
   written there.
2. **Present but incomplete** (issuer known, credential ID or dates missing):
   include only the parts that are recorded. "CompTIA Security+ (active)" is
   fine. Never pad it with a bracketed placeholder.
3. **Not in the master resume at all, or recorded with no substantive detail**:
   **omit the entry entirely** and report it in Phase 7 as a real, unmet
   requirement, with the exact line the candidate should add to
   `input/master-resume.md` to close it on future runs.

Rule 3 applies even when the master resume's own notes ask for a bracketed
placeholder. Omission achieves what those notes want, which is preventing
fabrication, without putting an unsubmittable placeholder in the deliverable.
The gap is still surfaced, just in chat rather than in the PDF.

The same rule covers licences, clearances and any degree whose discipline,
institution or year is unrecorded.

---

# PHASE 5: CONTENT GENERATION

## 5.1 Headline

The single line under the name. Rules:

- It is **the JD's job title, verbatim**, or as close as the candidate's real
  seniority allows.
- One line. No pipes. No module list. No technology list. Under 60 characters.
- `target-role` in the metadata must match it. The headline gate compares them
  and fails the build if the distinctive words do not carry over.

Good: `SAP Solution Architect`. Bad: `SAP Solution Architect | FI/CO & Order
Management (SD/MM) on ECC 6.0 / HANA | ABAP Development, IDoc & SAP BTP/CPI
Integration`.

If the candidate's real seniority does not support the JD's level, use the title
without the inflated seniority word rather than claiming it.

## 5.2 Summary

One paragraph, or two at most. 60 to 110 words total.

Structure: years and primary expertise, then the specific platform or domain
overlap with this JD, then the delivery record that proves it. Lead with what
this employer is hiring for, not with a generic self-description.

No bold. No metrics that are not in the master resume.

## 5.2b Literal keyword coverage

Keyword scanners match strings, not meaning. A resume can describe a skill
perfectly and still score zero for it. Real misses found on a live check:

- The posting's industry tags read "Artificial Intelligence, Cloud, Software".
  The resume said "AI-driven analytics", "RAG", "AWS" and "Microsoft Azure", and
  scored **zero** for both *Artificial Intelligence* and *Cloud*, because neither
  literal string appeared anywhere.
- The posting wanted vendor management. The resume said "vendor intake and
  evaluation" and scored zero for *vendor management*.

So, for every must-have and every industry tag:

- **Write the exact string the JD uses, at least once.** Naming AWS does not
  cover "cloud". Naming LangChain does not cover "artificial intelligence".
- **Give both the spelled-out form and the acronym** on first use: "Mobile device
  management (MDM)", "Information technology (IT) operations",
  "Artificial intelligence (AI)". One mention of each form is enough.
- **Use the generic category name alongside the product name.** "ServiceNow" is
  the tool; "ITSM" and "IT service desk" are what the scanner looks for.
- A skill-category label is itself indexed, so make the labels carry keywords:
  `Vendor Management` beats `Vendor and SaaS Lifecycle`.
- Say years of experience **in digits**: "9+ years", never "nine years".

Only claim what the master resume supports. This section is about wording what
is already true in the language the scanner expects, never about adding claims.

## 5.3 Technical Skills

**One skills section. There is no Core Competencies section.** Two overlapping
skill lists is the defect this replaces.

- Six to eight categories, never more. The gate fails at nine.
- Format: `- **Category Label**: value, value, value`
- **Labels must be 26 characters or fewer.** All labels share one column sized
  to the widest of them, so a single long label pushes every value on the page
  to the right and leaves the short labels sitting in a void. The gate enforces
  this. "Vendor and SaaS Lifecycle" fits; "SaaS Lifecycle and Vendor Management"
  does not.
- Category labels are short and concrete, named for what this employer cares
  about ("SAP BASIS and Security", not "Enterprise Platform Ecosystem").
- Order categories by JD relevance. Order values within a category the same way.
- Plain comma-separated values, no nesting, no parenthetical essays.
- Include both spelled-out and acronym forms where an ATS might want either:
  "Kubernetes (K8s)".
- Aim for 8 to 16 values per category. A category listing 40 technologies reads
  as a keyword dump and costs you the page budget.

## 5.4 Professional Experience

- Include every role from the master resume. Reorder by relevance only if the
  chronology allows it.
- 4 to 6 bullets per role, most JD-relevant first.
- Keep the real job titles from the master resume. Reframing what the work
  emphasises is tailoring; renaming the role is fabrication.
- Company, dates and location come from the master resume unchanged. The frozen-
  facts gate verifies each one.

Bullet shape: what you did, what you built or changed, and what happened as a
result. Lead with a strong verb. Include a real number where the master resume
has one, and do not manufacture one where it does not.

**Measurable results.** Screeners look for about five quantified outcomes, and
the verifier reports how many the resume carries. Use every real number the
master resume holds before falling back to qualitative phrasing. If the master
resume genuinely has fewer than five, **do not close the gap by inventing one**.
Report the shortfall in Phase 7 and name the specific bullets that would carry a
number, so the candidate can supply the real figures for future runs. A
fabricated metric is the single easiest thing for an interviewer to disprove.

Good: `Owned production support for live systems, investigating and resolving
complex defects, shipping enhancements and improving application responsiveness
by 30%.`

Bad: `Worked on performance improvements.` (says nothing)
Bad: `**Owned production support** for **live systems**...` (bold, blocked by gate)

There is no separate Leadership & Impact section. Leadership belongs in the
bullets of the role where it happened.

## 5.5 Education, Certifications, Open Source

- **Education**: entries with a complete degree, institution, dates and location.
  Coursework as one plain line under the entry when it is relevant. Any degree
  missing its discipline, institution or year is omitted and reported, per
  Phase 4.
- **Certifications**: per Phase 4. One per bullet, plain text, no pipes, no bold.
- **Open source and publications**: include only when the JD makes them relevant
  and the page budget allows. They are the first thing to cut.

---

# PHASE 5.8: COVER LETTER

Generated from the Phase 1 analysis and the finished resume, not written from
scratch. Every claim, project or metric must already appear in the resume or the
master resume.

1. Header block identical in form to the resume, with `kind: cover` in the
   metadata.
2. Date, `Month DD, YYYY`.
3. Recipient: `Hiring Manager` (or a named contact from the JD) and the company.
4. Salutation.
5. Opening, 2 to 3 sentences: the exact role, and one hook connecting the
   candidate's background to it.
6. Body, 1 to 2 paragraphs: 2 to 3 concrete achievements taken from the resume,
   chosen against the JD's must-haves. Weave in keywords as ordinary prose.
7. Closing, 2 to 3 sentences: fit, one concrete detail about this company from
   the JD, and an interview call to action.
8. `Sincerely,` and the full name.

250 to 400 words. First person, active voice. Same house style as the resume: no
bold, no em dashes, no AI register. A letter generic enough to send unmodified to
another company has failed this step.

---

# MASTER RESUME SYNC

`input/master-resume.md` is the single source of truth across runs. The track
files are filtered views of it.

**The skill no longer writes JD-detected skills into any master resume.** Those
go to `data/new-skills-{worktree}.md` and the candidate applies them by hand.
A JD mentioning a skill is not evidence the candidate has it, and the confirming
question that used to justify the write is gone.

**Sync only when the user volunteers a real fact in conversation**: a real metric
for a previously unquantified achievement, real experience not in the file, a
certification with issuer and dates, or a correction to a parsed fact. That is a
statement by the candidate about themselves, which is a different thing from a
keyword found in a posting.

**How**: edit `input/master-resume.md` directly, matching its existing structure.
Then mirror it into any track file the skill belongs to, so the views stay
consistent with the master. Mention both edits in the Phase 7 report. If the user
provides nothing, proceed without fabricating and without chasing them for it.

---

# PHASE 6: VERIFICATION

Self-review does not catch these defects, which is why they recurred for months.
Run the gates:

```
python scripts/verify_resume.py {YYYYMMDD}/{company}-{position}-{name}
```

Five gates, all blocking:

| Gate | Catches |
|---|---|
| human style | em dashes, arrows, emoji, AI phrasing, bracketed placeholders |
| frozen facts | a company, date, location, school or contact value not found in the master resume |
| headline | a headline that does not track `target-role`, or is a multi-part title |
| emphasis budget | inline bold anywhere except a skill label |
| structure & length | missing or forbidden sections, malformed entries, too many skill categories, skill labels over 26 chars, over 1050 words |

`convert_resume.py` runs the same gates plus a page-count check and writes no PDF
if any fails. **Fix the markdown until the gates pass. Never reach for
`--no-verify` to get past a failure** — that flag exists for inspecting a
work-in-progress layout, not for shipping.

Beyond the gates, check by reading:

- Every must-have JD keyword appears at least once, and no keyword more than
  three times.
- Every metric traces to the master resume.
- The most relevant experience is positioned first.
- Read the summary and three bullets aloud. If any sounds like a press release,
  rewrite it.

---

# PHASE 7: OUTPUT AND HANDOFF

Save both files to `output/{YYYYMMDD}/`:

- Resume: `{company}-{position}-{name}.md`
- Cover letter: `{company}-{position}-{name}-cover.md`

Then report in chat, not in the files:

```
## OPTIMIZATION SUMMARY

**Target**: [Company] - [Position] - [Level]
**JD read from**: [input/jd-{worktree}.txt, or "input/jd.txt (fallback: input/jd-{worktree}.txt not found)"]
**Tracks used**: [primary track, then any secondary, or "none matched, used master-resume.md"]

### Coverage
- Must-have keywords covered: [X/Y]
- Nice-to-have keywords covered: [X/Y]
- Resume length: [N] words, [N] pages

### Not claimed
JD requirements with no support in the master resumes, deliberately left out:
- [keyword] - [why, and what would close it]

### Omitted for missing detail
Entries dropped because the master resume records the claim but not the facts:
- [e.g. SAP certification: recorded as held, but no certification name, module,
  date or credential ID. Add those to Section 12 to include it next run.]

### Files written for weekend review
- data/new-skills-[worktree].md: [N] skills across [N] tracks, or "nothing new"
- data/master-resume-gaps-[worktree].md: [N] entries, or "no gaps"

### Master resume updates
- [Facts the user volunteered this run and where they were written, or "None"]

### Gaps to review
- [Anything the candidate should verify before submitting]
```

Then the handoff:

```
Resume and cover letter are ready.

- Resume: [path]
- Cover letter: [path]
- New skills logged: [path, or "none this run"]
- Gaps logged: [path, or "none this run"]

Before submitting:
1. Verify every achievement and date reads true to you.
2. Read the cover letter aloud, and adjust the tone if it does not sound like you.
3. Review any master-resume edits made this run.

The two data files are for whenever you get to them, not for now.

python scripts/convert_resume.py "{YYYYMMDD}/{company}-{position}-{name}"
```

That command converts both files: it finds the paired `-cover.md` automatically.
Print it filled in with the real path, as the literal last line. The user runs it
themselves; this skill never runs it for them.

Then go straight to Phase 8, in the same turn.

---

# PHASE 8: POST-DELIVERY QUESTIONS

Help the candidate answer whatever else the posting or application form asks,
grounded in the resume just generated.

## Step 1: ask

A single plain open question, not a multi-select, since the space is unbounded:

```
Any other questions from the posting or application - screening questions,
"why do you want this role" prompts, short-answer fields? Paste them and I'll
draft answers grounded in the resume above. If not, you're all set.
```

If the user indicates they are done, stop. Do not ask again this session.

## Step 2: answer

- **Ground every claim in the generated resume** or `input/master-resume.md`.
  Never introduce a fact, project or metric that is not in one of those two files.
- **Write like the candidate.** 2 to 5 sentences for a typical screening
  question, longer only when the question asks for depth. No corporate filler, no
  restating the question, no bullet lists unless asked, no AI-disclaimer hedging.
  Same house style: no em dashes, no AI register.
- First person.
- If a question cannot be answered without fabricating (salary expectations,
  availability, visa status, a fact simply not recorded), say so plainly and ask
  the user for the real answer.
- If the user volunteers a real new fact while answering, offer to fold it into
  `input/master-resume.md` per MASTER RESUME SYNC.

## Step 3: repeat

Return to Step 1 after each batch until the user is done.

---

# EDGE CASES

| Scenario | Action |
|---|---|
| JD names a tech skill not in any master resume | Log it to the new-skills file. Do not use it this run. Do not ask |
| Skill missing after Phase 1.5 | Bridge via closest adjacent skill, else omit and flag in the report and gaps file |
| JD spans several kinds of work | Select up to three tracks, rank them, let the primary drive the document |
| No track matches the JD | Generate from `input/master-resume.md` alone and log it to the gaps file |
| Smart-contract, protocol or audit role | Never source from `master-resume-blockchain.md`. Log the mismatch |
| A track file contradicts `input/master-resume.md` | Facts follow the master. Log the drift |
| The candidate clearly does not qualify | Still generate, honestly and without inflation. Log why in the gaps file. Never refuse and never ask |
| `data/` does not exist | Create it. Never skip a log write because the directory is missing |
| Sessions running at once | Each reads its own `input/jd-{worktree}.txt` and appends to its own `{worktree}`-named data files. Read before appending |
| `input/jd-{worktree}.txt` missing, `input/jd.txt` present | Use the fallback, name the expected path in the report, warn that it is unsafe with concurrent sessions |
| Both JD paths missing | Stop and report the paths checked. The only condition that halts a run |
| Only another worktree's `jd-*.txt` exists | Do not read it. Treat as "both missing" |
| JD requires a certification the candidate lacks | Omit it. Report as an unmet requirement. Never generate one |
| Master resume records a credential but not its details | Omit the entry, report exactly what to add to close it |
| Missing metric | Honest qualitative phrasing or a clearly-scoped estimate. Never a fabricated number |
| Resume runs over two pages | Cut the least JD-relevant skill categories first, then the weakest bullet in each role, then optional sections |
| A gate fails | Fix the markdown. Do not use `--no-verify` |
| Combination role | Prioritise the primary, keep the secondary visible in skills |
| Junior candidate, senior posting | Do not inflate the headline. Highlight relevant depth |
| Section 2 core skills are irrelevant to this JD | Prefer them within the eight-category budget, but do not blow the budget to include them all |
| Company name unresolvable from the JD | Same placeholder in the cover letter recipient; flag it in the report |
| User supplies a real fact mid-session | MASTER RESUME SYNC, then use it |
| Extra question needs a fact nobody recorded | Say so and ask. Do not guess |

---

# CORE CONSTRAINTS

**No fabrication**
- Never invent experience, dates, companies, job titles, certifications or metrics
- Never claim a JD-only skill. Detecting one and logging it is not evidence the
  candidate has it
- Reorder, reframe and select from existing content, nothing more
- Persist facts the user volunteers into `input/master-resume.md` and the matching
  track file, rather than asking about them again next run

**Never block on a question**
- Produce the resume and cover letter on every run, whatever the JD asks for.
  The sole exception is a missing job description, which is a missing input
  rather than an uncertainty (Phase 0)
- Uncertainty goes to `data/master-resume-gaps-{worktree}.md`, not to the user
  mid-run
- Newly detected skills go to `data/new-skills-{worktree}.md`, not to a prompt
- The only question in the workflow is Phase 8, after both files are delivered

**Authenticity**
- Do not distort an achievement to fit the JD
- Do not oversell impact
- What the candidate cannot defend in a technical screen does not go on the page

**Honesty about gaps**
- Unmet requirements are reported in chat every run, never hidden behind a
  keyword list narrowed until it scores 100%
- Nothing marked as AI-generated ever reaches the deliverable
