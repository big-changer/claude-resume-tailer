# Step 8: Deferred Logging

Read this only at Step 8, after the resume and cover letter exist on disk and the report
has been printed. Nothing here changes what was delivered.

Both logs live in a directory named for the run slug:

```
data/{slug}/new-skills.md
data/{slug}/master-resume-gaps.md
```

## Ground rules

- **Do not `mkdir` the directory.** The Write tool creates missing parents, so shelling out
  only stops the run for a permission prompt. Same for `ls` to see whether the files exist:
  read them and treat "not found" as "first run for this slug".
- **Append. Never rewrite, reorder, or delete an earlier run's entries.** These files are
  the candidate's weekend review queue.
- Read a file before appending so a skill already recorded for the same track is not logged
  twice. If it is already there, add this JD to its `Seen in:` line instead of creating a
  second entry. On the first run for a slug the read fails, which is expected.
- Every append opens with a run header, and entries under it are grouped by track using the
  track's display name as a `### ` heading:

```markdown
## 2026-08-02 | Accuris | SAP Solution Architect
```

- If a run has nothing to add to a file, do not touch that file and do not write an empty
  run header.

---

## new-skills.md

JD skills with no match in any track file. Keyword-spotting against a JD is noisy: it
over-triggers on generic words, on near-duplicates of skills already listed under another
name, and on technologies the JD mentions in passing. Writing any of that into a track file
would fabricate a claim, so this is a note to the candidate, never an edit.

### Build the list

1. Take the JD's key technologies and must-have / nice-to-have skills.
2. Normalise them against Section 1 of every selected track, case-insensitively, collapsing
   well-known aliases (".NET" / ".NET Core" / "dotnet", "JavaScript" / "JS", "Postgres" /
   "PostgreSQL"). An alias is not a new skill.
3. Drop generic non-skill noise: "software", "programming", "experience", "team player",
   "communication skills".
4. Whatever survives needs checking against the tracks this run did not select. **Do this
   in one Grep call with a regex alternation**, not a shell loop:

   ```
   pattern: (?i)\b(kafka|kinesis|flink|streaming|alerting|on-call|slo)\b
   glob:    input/master-resume-*.md
   output:  content, with -n
   ```

   Batch 10 to 20 terms per call, and escape regex metacharacters (`C++` becomes `c\+\+`,
   `.NET` becomes `\.net`). Ignore any hit in `master-resume-bone.md`. A shell loop with
   `$t` in it cannot be pre-approved, so it stops the run for a confirmation on every batch.
5. Classify each term from what that one Grep returned:
   - **Evidenced in `input/projects.md` or in a selected track's Sections 2 to 4 but not itemised in its Section 1**:
     an itemisation gap.
   - **Absent from every selected track but present in an unselected one**: a filtering gap.
   - **Not evidenced in any track file**: a genuinely new claim.
6. Rank must-haves first, then nice-to-haves, ties broken by JD emphasis.

If nothing survives, write nothing.

### Entry format

Group by the track the skill would belong to, chosen from the skill's subject matter rather
than from which track happened to be selected this run: a Kubernetes skill is logged under
Cloud / DevOps Engineer even on a JD that selected only Full Stack.

```markdown
## 2026-08-02 | Accuris | SAP Solution Architect

### Enterprise Platform Engineer

- **SAP BTP Integration Suite** - must-have, JD says "3+ years hands-on with BTP
  Integration Suite". Status: not evidenced in any track file.
  Nearest recorded: SAP CPI, SAP PI/PO. Seen in: Accuris SAP Solution Architect.
- **CDS views** - nice-to-have. Status: evidenced in an input/projects.md entry but not
  itemised in Section 1. Nearest recorded: ABAP, HANA modelling.
  Seen in: Accuris SAP Solution Architect.

### Cloud / DevOps Engineer

- **Azure DevOps release gates** - nice-to-have. Status: filtering gap, present in
  master-resume-fs.md but absent from master-resume-devops.md.
  Seen in: Accuris SAP Solution Architect.
```

Required per entry: the skill name, must-have or nice-to-have, the status from step 5, the
nearest thing already recorded, and the JD it was seen in.

### What this does not do

- A skill logged as **not evidenced in any track file** was correctly omitted from the
  resume. Logging is a note to the candidate, not a confirmation, and it is never grounds to
  revise the delivered file.
- Do not edit any track file to add a detected skill. That decision is the candidate's, and
  they make it against the file, not mid-run.

---

## master-resume-gaps.md

Answers one question for the candidate at the weekend: *what would have made this run
produce a better resume?* Log any of these:

| Situation | Example entry |
|---|---|
| A must-have with no support anywhere | Kubernetes operators: JD must-have, nothing recorded. Would need a real example to claim. |
| Fewer than five quantified results available | Only 2 real metrics exist for this track. Bullets X and Y would carry numbers if the candidate supplied them. |
| A recorded claim too thin to use | SAP certification recorded as held, but no name, module, date or ID, so the entry was omitted. |
| A track file too thin for the JD it was selected for | master-resume-ai.md itemises RAG and embeddings but records no delivery project, so the JD's "describe an LLM system you shipped" cannot be answered. |
| Drift between two track files | OpenAPI is in master-resume-enterprise.md but not in master-resume-fs.md. Add it to both, or to neither. |
| Two track files disagree on a fact | master-resume-ai.md lists coursework master-resume-fs.md does not. Used the primary; reconcile the two. |
| A structural or positioning problem | JD wants 15+ years systems engineering; record supports ~9y7m software. Cannot be closed by wording. |
| No track matched the JD | Fire protection engineering posting; generated from master-resume-fs.md as the general fallback. |
| Anything that forced a judgment call | Two employers plausible for this project; picked the later one on date overlap. |

Write what would fix it, not just what was wrong. "Add the state and licence number to
Section 2 of each track file" is useful; "PE licence incomplete" on its own is not.

---

## Master resume sync

The record spans three kinds of file: `input/profile.md` for the shared facts,
`input/projects.md` for the project record, and `input/master-resume-{track}.md` for the
per-track skills, certificates, open source and behavioural examples. Each fact lives in
exactly one of them, so a correction lands in one place.

**The skill never writes JD-detected skills into a track file.** Those go to
`new-skills.md` and the candidate applies them by hand. A JD mentioning a skill is not
evidence the candidate has it.

**Sync only when the user volunteers a real fact in conversation:** a real metric for a
previously unquantified achievement, real experience not in the files, a certification with
issuer and dates, or a correction to a parsed fact. That is a statement by the candidate
about themselves, which is a different thing from a keyword found in a posting.

| What the user gave you | Where it goes |
|---|---|
| A skill | Section 1 of every track it genuinely belongs to, usually one or two files |
| A fact: employer, title, date, location, education, contact | `input/profile.md`, once. It is the single source and the gate reads it |
| A certificate | Section 2 of every track file it belongs to, worded identically |
| A behavioural example | Section 4 of the tracks it is relevant to, framed for each. Do not paste the same wording into all five |
| A project, or a metric belonging to one | `input/projects.md`, once. It is shared, so never copy it into a track file |

Never `master-resume-bone.md`; it is the anonymised sharing template and holds no real data.

Facts are single-source now, so the old half-applied-edit failure cannot happen to them:
write the employer or date to `input/profile.md` and every track sees it.

What can still drift is Sections 2 and 3. Certificates and open-source contributions are
facts that happen to live per-track, so they are meant to read identically everywhere: one
added to a single track and not the others is drift, and it is worth logging.

**Section 4 is different, and its differences are not drift.** The behavioural examples are
deliberately written per track, drawing the same underlying evidence toward what that kind
of role screens for. Never reconcile them, and never copy one track's version over
another's. If a track's Section 4 is thin or off-target for the JD, log that, not the fact
that it differs.

If two sessions both need a sync write, apply one edit at a time and re-read the file
before the second.

List every file touched in the report. If the user provides nothing, proceed without
fabricating and without chasing them for it.
