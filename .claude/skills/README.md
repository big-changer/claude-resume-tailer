# Claude Skills - Resume Generator Suite

Shareable Claude skills for the resume-generator project.

---

## Available skills

### Resume-JD Optimizer

**File**: `resume-jd-optimizer/SKILL.md`

Reads a job description and the candidate's per-track master resumes, then
writes a tailored two-page resume and a matching cover letter that read as if a
person wrote them.

Invoked with a **run slug**, which namespaces the posting and the logs so two
sessions can work different jobs in the same checkout:

```
/resume-jd-optimizer hiringcafe
```

**Input**
- `input/jd-{slug}.txt` - job description, one per slug
- `input/master-resume-{track}.md` - the only resume sources. Each is complete on
  its own, skills and facts, and the tracks are selected from the JD's role
  responsibilities. There is no combined `master-resume.md`
- `input/master-resume-bone.md` is the anonymised sharing template, never a source

**Output**
- `output/{YYYYMMDD}/{company}-{position}/{name}.md`
- `output/{YYYYMMDD}/{company}-{position}/{name}-cover-letter.md`
- `data/{slug}/new-skills.md` - JD skills with no match in any track file
- `data/{slug}/master-resume-gaps.md` - what would have made this run better
- A chat-only report covering keyword coverage, requirements deliberately not
  claimed, and entries omitted for missing detail

**What it does**
- Extracts requirements, keywords and the exact job title from the JD
- Reads the JD's role responsibilities and selects the matching per-track master
  resumes, so a hybrid posting can draw on two or three at once
- Takes skills from every selected track and facts from the primary one, then
  scores each role for relevance
- Generates the summary, one technical-skills section, experience bullets,
  education and certifications against a two-page budget
- Generates the cover letter from the finished resume, not from scratch
- Answers follow-up screening questions after delivery

**It never stops to ask.** The resume is produced on every run. Skills the JD
names but the record cannot support are appended to `data/{slug}/new-skills.md`,
and anything that weakened the run goes to `data/{slug}/master-resume-gaps.md`,
both grouped by track for weekend review. The slug comes from the invocation, so
two concurrent sessions in one checkout do not collide.

The one condition that halts a run is a missing `input/jd-{slug}.txt`. There is
no `input/jd.txt` fallback, because sharing one posting between concurrent runs
is the failure the slug exists to prevent.

**What it deliberately does not do**
- No keyword bolding. Bold is invisible to an ATS and 250 bold runs on a page
  cancel each other out for a human reader, so bold is reserved for structure.
- No generated certifications, and no AI-generated markers. A credential the
  track files do not record is omitted and reported as a real gap.
- No bracketed placeholders in the deliverable. An entry missing its facts comes
  out of the resume and goes into the chat report instead.

---

## Quality gates

The output is checked by `scripts/verify_resume.py`, and
`scripts/convert_resume.py` writes no PDF unless every gate passes.

| Gate | Catches |
|---|---|
| human style | em dashes, arrows, emoji, AI-register phrasing, bracketed placeholders |
| frozen facts | a company, date, location, school or contact value not found in any `input/master-resume-*.md` track file |
| headline | a headline that does not track the target job title, or is a multi-part title |
| emphasis budget | inline bold anywhere except a technical-skill label |
| structure & length | missing or forbidden sections, malformed entries, too many skill categories, skill labels over 26 chars, over 1050 words |

Plus a page-count check at render time: two pages for a resume, one for a cover
letter.

Run them on their own with:

```bash
python scripts/verify_resume.py 20260801/accuris-sap-solution-architect/gafari-arowojebe
```

The gates are the real specification. They exist because a prose checklist that
the generating model ticks off itself did not stop the same defects recurring.

---

## Output contract

The generated markdown is parsed structurally, so it is not free-form. The full
contract lives in the docstring of `scripts/convert_resume.py` and is restated
in the skill. In short:

```markdown
<!--
target-company: Accuris
target-role: SAP Solution Architect
kind: resume
-->

# Gafari Arowojebe
SAP Solution Architect
email | phone | location
linkedin | github

## Summary

One paragraph, or two at most.

## Technical Skills

- **Category Label**: value, value, value

## Professional Experience

### Job Title | 02/2024 - 03/2026 | Las Vegas, NV
#### Company Name

- One achievement per bullet.

## Education

### Degree | 07/2012 - 05/2017 | St. Paul, MN
#### Institution

## Certifications

- One per line
```

Blank lines and `---` are ignored by the renderer. Spacing is structural, so two
runs produce the same rhythm regardless of how the markdown was spaced.

---

## Usage

```bash
# 1. Put the posting in input/jd-{slug}.txt, e.g. input/jd-hiringcafe.txt
# 2. Run the skill with that slug:  /resume-jd-optimizer hiringcafe
# 3. Convert, which also converts the paired cover letter
python scripts/convert_resume.py "20260801/accuris-sap-solution-architect/gafari-arowojebe"
```

`--no-verify` renders without the gates. It is for inspecting a work-in-progress
layout, never for shipping past a failure.

Requires `reportlab` (see `requirements.txt`). The PDF uses Times, a core PDF
font, so there is no font directory to configure.

---

## Design rationale

- **Two pages, roughly 900 words.** A five-page resume is not read.
- **Greyscale, one typeface, hairline rules.** Colour, icon glyphs and shaded
  tables read as generated-by-a-tool.
- **One skills section.** Two overlapping skill lists was the defect this
  replaces.
- **Structural spacing.** Layout never depends on how many blank lines the
  generating model happened to emit.
- **One left edge.** Every element, headings, paragraphs, skill labels, job
  titles and bullet markers, starts at the same margin, and right-aligned dates
  end exactly at the opposite one.
- **Clickable contact details.** Bare URLs and emails become real PDF links,
  with the visible text left untouched so an ATS still reads the plain address.
- **Honest gaps.** A resume scoring 100% against a keyword list the candidate
  cannot defend in a technical screen is worse than one scoring 80% honestly, so
  unmet requirements are reported on every run.

Research basis (2024-2026): modern ATS use ML for contextual relevance scoring
and detect keyword stuffing; quantified metrics parse as structured data and
score higher; keywords work best integrated one to three times; simple
formatting parses most reliably.

Sources:
- [Scale.jobs ATS Algorithms](https://scale.jobs/blog/understanding-ats-scoring-algorithms)
- [ATS Resume Optimization 2025](https://scale.jobs/ats-resume-optimization-guide)
- [JobWizard Keywords](https://jobwizard.ai/blog/ats-resume-keywords-for-software-engineers)

---

## Sharing

Copy the `.claude/skills` directory alongside `scripts/verify_resume.py` and
`scripts/convert_resume.py`. The skill and the gates are a matched pair: the
skill writes to a contract that only those scripts enforce, so sharing one
without the other loses the guarantees.

```
.claude/skills/
├── resume-jd-optimizer/SKILL.md   the skill
├── README.md                      this file
├── SHARING-GUIDE.md
└── manifest.json                  metadata
```
