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

## Why the skill labels are capped at 26 characters

All labels share one column sized to the widest of them, so a single long label pushes
every value on the page to the right and leaves the short labels sitting in a void. It is a
layout constraint, not a style preference. "Vendor and SaaS Lifecycle" fits;
"SaaS Lifecycle and Vendor Management" does not.

## Why there is no inline bold

Bold is used in exactly one place: the label of a technical-skill row.

Bolding keywords buys nothing at the ATS layer, which reads the plain text either way, and
250 bold runs on a page cancel each other out as emphasis. The document is scanned by a
human in about 40 seconds; structure does that work, not typographic shouting. There is no
keyword-emphasis pass in this skill.

## Hard numbers enforced by `verify_resume.py`

| Limit | Value |
|---|---|
| Resume words | 1050 max, roughly 900 target |
| Cover letter words | 430 max, 250 to 400 target |
| Skill categories | 8 max |
| Skill label length | 26 characters max |
| Resume pages | 4 max in the verifier, 2 in practice |
| Cover letter pages | 1 |

## Cover letter shape

Same header block as the resume plus `kind: cover` in the metadata, then date, recipient,
salutation, body paragraphs and sign-off as plain prose. No sections, no bullets.
