---
name: resume-ats-checker
description: Read-only ATS scoring — takes a resume path (or application folder, or slug) and an optional --min flag, finds the job description beside it, and reports an ATS compatibility score, keyword match analysis, and gaps. Never edits, rewrites, or generates resume content.
---

# Resume ATS Checker

Scores how well a resume will pass Applicant Tracking Systems for a specific job description.

## Hard rule — read only

This skill is **analysis only**. It NEVER:
- Edits, rewrites, or reformats the resume or any project file
- Generates replacement bullets, summaries, or suggested wording
- Offers to apply fixes, or asks "shall I apply these changes?"
- Calls Edit, Write, or any file-modifying tool

Output is a report in the chat, and nothing else. If the user wants changes applied,
point them to the `resume-jd-optimizer` skill and stop.

## Arguments

Invoked as `/resume-ats-checker {path} [--min]`.

`{path}` is any one of:

| Form | Example |
|---|---|
| **Application folder** (usual) | `output/20260912/stillwater-insurance-group-java-software-engineer-i` |
| Folder slug alone | `stillwater-insurance-group-java-software-engineer-i` |
| Resume file | `output/20260912/stillwater-insurance-group-java-software-engineer-i/washington-demarcus-lewayne.md` |

The application folder path is the expected everyday form.

### Report mode

`--min` is an optional second argument. It changes **only how much is printed** — the
analysis in Steps 1 to 3 runs identically either way.

| Mode | Flag | Prints |
|---|---|---|
| Full (default) | none, or `--full` | Scores, formatting issues, the keyword table, missing and buried keywords, verdict |
| Minimal | `--min` | The score block only |

Anything other than `--min` / `--full` in that position is not a mode — treat it as part
of the path. Unknown flag, stop and say so rather than guessing the mode.

### Step 0 — Resolve the pair

Application folders are `output/{YYYYMMDD}/{company}-{position}/` and hold the resume,
the cover letter, and `jd.md` — the posting archived verbatim by `resume-jd-optimizer`.
Both sides of the comparison come from one folder, so resolve the folder first.

1. **Find the folder.**
   - Path to a file → its parent directory.
   - Path to a directory → that directory.
   - Bare slug → Glob `output/*/{slug}/`. Exactly one match, use it. Several (the same
     role run on different dates), use the newest date and say so in the report. None, stop.
   - A `.pdf` path → the folder is still its parent; score the `.md`, not the PDF.
2. **Find the resume.** In that folder, the `.md` whose metadata comment is `kind: resume`.
   By name that is `washington-demarcus-lewayne.md` — never the `-cover-letter.md` and
   never `jd.md`.
3. **Find the JD**, in this order:
   - `jd.md` in the same folder. This is the posting the resume was actually written
     against, so it is always preferred.
   - No `jd.md` (folders predating the archive step): read its `run-slug` is impossible,
     so fall back to `input/jd-{slug}.txt` **only if** the user named a slug explicitly.
     Otherwise stop and ask for the JD path — do not guess among `input/jd-*.txt`, and do
     not score against a posting from a different application.
4. **Report what you resolved** at the top of the output, so a wrong pairing is visible.
   Full mode only — under `--min` this block is omitted along with everything else that
   is not the score line:

```
Resume: output/20260912/{slug}/washington-demarcus-lewayne.md
JD:     output/20260912/{slug}/jd.md  (Company — Role)
```

When reading `jd.md`, ignore the leading `<!-- ... -->` metadata comment; the posting
text is everything after it. Same for the resume — `target-company` and `target-role`
in the comment are labels, not resume content, and are not keyword matches.

### No argument passed
Stop and ask which application to score. Do not scan `output/` and pick one.

### Pasted text instead of a path
Also fine — if the user pastes a resume and a JD directly, score them as given and skip
Step 0 entirely.

## Workflow

### Step 1 — Compatibility Check
Scan the resume for ATS-breaking elements:
- Tables, columns, text boxes, headers/footers
- Non-standard fonts (anything other than Arial, Calibri, Georgia, Times New Roman)
- Graphics, icons, logos, or images
- Non-standard section headers (e.g., "My Journey" instead of "Experience")
- Incorrect file format (should be .docx or text-based .pdf)
- Embedded hyperlinks that may not parse correctly

Reference for what counts as ATS-safe:
- Single-column layout
- Standard section names: Summary, Experience, Education, Skills, Certifications
- Dates in consistent format: MM/YYYY or Month YYYY
- No special characters in section dividers
- Bullet points using standard `•` or `-`

### Step 2 — Keyword Extraction (from job description)
Extract three keyword categories:
1. **Hard skills** — tools, technologies, certifications, methodologies
2. **Soft skills** — leadership, communication, collaboration
3. **Industry terms** — sector-specific jargon and role titles

Mark each as Required or Preferred based on how the JD frames it.

### Step 3 — Keyword Match Analysis
Compare extracted keywords against the resume:
- Match percentage per category, and overall
- Keywords missing entirely
- Keywords present but buried (appear only once, or only in a late bullet)
- Benchmark: **80%+ overall match** is the pass line

### Step 4 — Report

Print the shape the mode calls for, and nothing else.

**Minimal (`--min`)** — exactly this, no headings above it, no commentary below it:

```
ATS Compatibility: XX%   Keyword Match: XX%  (Hard XX% / Soft XX% / Industry XX%)   [PASS | BELOW 80%]
```

One line. No formatting issues, no keyword table, no verdict, no next steps. `PASS` when
the keyword match is 80% or higher, `BELOW 80%` otherwise. If the user wants the detail,
they rerun without `--min`; say that only if they ask.

**Full (default)** — the whole report:

```
### ATS Compatibility Score: XX%
### Keyword Match Score: XX%  (Hard XX% / Soft XX% / Industry XX%)

#### Formatting Issues
- [issue] — why it breaks parsing

#### Keyword Analysis
| Keyword | In Resume? | Where | Priority |
|---------|-----------|-------|----------|
| [kw]    | Yes / No  | [section or —] | Required / Preferred |

#### Missing Required Keywords
- [keyword]

#### Buried Keywords (present but low visibility)
- [keyword] — appears only in [location]

#### Verdict
[One paragraph: would this resume clear an ATS screen for this JD, and what is the single biggest gap.]
```

Stop after the report. Do not propose rewritten text.
