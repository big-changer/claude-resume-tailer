# Output Contract

Full renderer semantics for `scripts/convert_resume.py`. The skeleton in SKILL.md covers
the normal case; read this when something about the shape is unclear.

## Element table

| Element | Form | Renders as |
|---|---|---|
| Metadata | `<!-- key: value -->` at the top | stripped from the PDF, drives the headline gate |
| Name | `# Name` | centred, bold |
| Headline | the line directly under the name | centred italic, one line |
| Contact | the lines after that, until a blank | centred, one or two lines |
| Section | `## Title` | uppercase heading with a rule under it |
| Entry | `### Title \| dates \| location` | title bold left, dates and location grey right, same line |
| Entry subtitle | `#### Company` on the next line | italic grey under the title |
| Entry sub-heading | `#### Key Projects`, anywhere else in an entry | bold black, introduces the lines under it |
| Entry label | `**Tech Stacks**: values` | body line with a bold label |
| Skill row | `- **Label**: values` | two-column label and value |
| Bullet | `- text` | hanging indent, full width |
| Prose | a plain line | body paragraph |

## Rules the renderer depends on

- Dates are always `MM/YYYY - MM/YYYY`. The frozen-facts gate matches them against the
  track files, which write them as month names, so any real date will verify.
- Write URLs bare, as `linkedin.com/in/handle`, not as markdown links. The renderer turns
  bare URLs and email addresses into clickable links while leaving the visible text exactly
  as written, which is what an ATS reads. Square brackets are banned, so `[LinkedIn](url)`
  fails the gate anyway.
- Blank lines and `---` are ignored by the renderer. Spacing is structural. Do not try to
  control layout from the markdown.
- No markdown tables. No emoji. No HTML beyond the metadata comment.
- Required sections: Summary, Technical Skills, Professional Experience, Education.
  Optional: Certifications, Languages.
- Forbidden sections: Core Competencies, Key Skills, Core Skills, Leadership & Impact,
  Gap Analysis. The first three duplicate Technical Skills, the fourth restates the
  experience bullets, and the fifth belongs in chat.

## Where the skill labels come from

`input/skill-map.json` holds them, as a closed set of nine written verbatim. A run picks six
to eight of the nine and orders them by relevance to the posting; it never writes a label
the file does not list. All nine already fit the 26-character cap, so the cap binds only if
someone adds a tenth.

That cap exists because all labels share one column sized to the widest of them, so a single
long label pushes every value on the page to the right and leaves the short labels sitting
in a void. It is a layout constraint, not a style preference. "Vendor and SaaS Lifecycle"
fits; "SaaS Lifecycle and Vendor Management" does not.

## The shape of an experience entry

Four parts, in this order, enforced by `check_experience_shape` in `verify_resume.py`:

1. A plain summary line, 20 to 35 words. No bullet marker, no bold.
2. 3 to 5 achievement bullets.
3. `#### Key Projects`, then 2 to 3 project lines as `- Name - what it is`.
4. `**Tech Stacks**: values`, which closes the entry. Nothing follows it.

Both labels are fixed strings, spelled `Key Projects` and `Tech Stacks`. The gate matches
them literally, so a renamed label reads as a missing part rather than as a variation.

`#### ` means two different things by position, which is what lets the entry carry a
sub-heading without a fifth heading level. Directly under a `###` it is the company or
school, rendered italic grey; anywhere else it is a sub-heading inside the entry, rendered
bold black.

The Tech Stacks line has an evidence rule the Technical Skills section does not: every value
must sit on a `Skills used` line of a project belonging to that company. A Technical Skills
row may carry a `rules.unevidenced` value from `input/skill-map.json`, because the section
says what the candidate can do. This line says what one employer's work was built on, so the
same value there would be a claim about that job.

## Why there is almost no inline bold

Bold is used in two places, both structural labels: the label of a technical-skill row, and
the `Tech Stacks` label closing an experience entry.

Bolding keywords buys nothing at the ATS layer, which reads the plain text either way, and
250 bold runs on a page cancel each other out as emphasis. The document is scanned by a
human in about 40 seconds; structure does that work, not typographic shouting. There is no
keyword-emphasis pass in this skill.

## Hard numbers enforced by `verify_resume.py`

| Limit | Value |
|---|---|
| Resume words | 1050 max, roughly 900 target |
| Cover letter words | 430 max, 250 to 400 target |
| Skill categories | 8 max, 6 target minimum, drawn from the nine in `input/skill-map.json` |
| Skill label length | 26 characters max |
| Resume pages | 4 max in the verifier, 2 in practice |
| Cover letter pages | 1 |

## The archived job description

The application folder also holds `jd.md`, the posting copied verbatim from
`input/jd-{slug}.txt` under a `kind: jd` metadata comment. It is not a rendered document:
no gate runs against it, `convert_resume.py` ignores it when a folder path is passed and
refuses it when it is named directly. Nothing on this page constrains its content.

## Cover letter shape

Same header block as the resume plus `kind: cover` in the metadata, then date, recipient,
salutation, body paragraphs and sign-off as plain prose. No sections, no bullets.

The date line is the `letter` value from `python scripts/resume_date.py --json`, copied
exactly: `September 10, 2026`, full month name, no leading zero on the day. That script
reads the timezone of the resume location in `input/profile.md` section 4, so the letter is
dated by the candidate's calendar rather than by whatever clock the pipeline runs on. No
gate can catch a wrong date here, which is exactly why it is never typed from memory.
