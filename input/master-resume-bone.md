# Resume Extraction - [Full Name] ([Track Label] track)

Anonymised template for one `input/master-resume-{track}.md` file. Copy it per track.

This file holds only what varies by track. Two companion files hold the rest, and both are
shared by every track:

- `input/profile.md` - employers, titles, dates, locations, company descriptions,
  education, location, LinkedIn, GitHub, email, phone, and a concise structured profile.
  The frozen-facts gate reads this file, so every fact a resume uses must appear in it.
- `input/projects.md` - one entry per project, each with Company, Period, Tracks,
  Skills used, Measured results, and a prose description.

Never put a fact in this file that belongs in `input/profile.md`. It would be duplicated
across every track and drift.

---

## 1. All Available Skills

The category labels are a **closed set**, defined once in `input/skill-map.json`. Copy them
verbatim. Never invent a label for a track, never rename one, never merge or split one:

- Programming Languages
- Frameworks & Libraries
- Databases
- Cloud & DevOps
- Tools & Platforms
- Testing
- Architecture & Design
- Data & AI
- Methodologies

### [One label from the list above]

- [Value, copied from that label's `values` list in input/skill-map.json]
- [Value]

### [The next label]

- [Value]

Order the labels to put the categories this kind of role cares about first, and drop any
label with nothing this track can claim. This is an inventory, not a shortlist: list
everything genuinely claimable for this kind of role, and let the skill select against the
job description.

A value may appear under more than one label here, because which labels a resume renders
changes per posting. The resume places each value once. This inventory does not.

Close the section by repeating the `recorded_gaps` lines of every label used, so the limits
travel with the file. A skill that is not in `input/skill-map.json` does not go here: add it
to that file first, and only once `input/projects.md` records a project behind it.

---

## 2. Certificates

- [Certificate Name] | [Issuing Organization] | Obtained: [MM/YYYY] | Expires: [MM/YYYY] |
  Credential ID: [ID]

[Or: "No formal certificates or certifications are listed."]

---

## 3. Open-Source Contributions

[List repos, packages, or public contributions, with links if available.
Or: "No explicit open-source contributions."]

---

## 4. Behavioral / Behavioural Section

### Ownership & Initiative

- [Example demonstrating this competency]

### Problem Solving

- [Example demonstrating this competency]

### [Other competency, e.g. Leadership / Collaboration / Communication]

- [Example demonstrating this competency]

### Results Orientation

- [Quantified outcome, e.g. "Reduced X by Y%"]
- [Quantified outcome]

---

## Source

[Where this was extracted from, e.g. "Extracted from the provided resume."]
Shared facts: input/profile.md. Projects: input/projects.md.
