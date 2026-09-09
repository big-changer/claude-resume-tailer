# House Style

Read this while writing prose, or when the human-style gate fails and the CHECKLIST in
SKILL.md did not explain why.

## Write like a person, not like a model

- **No em dashes, en dashes, arrows, ellipsis characters, curly quotes, bullet glyphs,
  non-breaking spaces or zero-width spaces.** Use a comma, a colon, a full stop, or a new
  sentence. The gate blocks the build on any of them, and they are the single loudest tell
  that a machine wrote the document.
- **No AI register.** The verifier matches these as substrings, so inflected forms fail
  too: leverag, delve, seamless, robust and scalable, spearhead, cutting-edge, fast-paced
  world, showcas, underscor, it's worth noting, not only, tapestry, pivotal, meticulous,
  realm of, harness the power, in today's, furthermore, moreover, state-of-the-art,
  game-chang, unlock the, elevate the, myriad, testament to, navigate the complex, synerg,
  at the forefront. Say the plain thing instead.
- **No square brackets anywhere in the output.** Not for placeholders, not for
  `[AI-Generated]` markers, not for `[to be supplied by candidate]`. If a fact is not
  available, the entry is omitted from the resume and reported in chat.
- Short declarative sentences. One idea per bullet. A number where a real number exists,
  and plain language where one does not.

## Two pages, hard

Budget is roughly 900 words and never above 1050. Anything that does not earn its place
against this specific job description comes out. A resume that runs to five pages is not
read. Cut in this order: the least JD-relevant skill categories, then the weakest bullet in
each role, then optional sections.

## Literal keyword coverage

Keyword scanners match strings, not meaning. A resume can describe a skill perfectly and
still score zero for it. Real misses found on a live check:

- The posting's industry tags read "Artificial Intelligence, Cloud, Software". The resume
  said "AI-driven analytics", "RAG", "AWS" and "Microsoft Azure", and scored **zero** for
  both *Artificial Intelligence* and *Cloud*, because neither literal string appeared
  anywhere.
- The posting wanted vendor management. The resume said "vendor intake and evaluation" and
  scored zero for *vendor management*.

So, for every must-have and every industry tag:

- **Write the exact string the JD uses, at least once.** Naming AWS does not cover "cloud".
  Naming LangChain does not cover "artificial intelligence".
- **Give both the spelled-out form and the acronym** on first use: "Mobile device
  management (MDM)", "Information technology (IT) operations", "Artificial intelligence
  (AI)". One mention of each form is enough.
- **Use the generic category name alongside the product name.** "ServiceNow" is the tool;
  "ITSM" and "IT service desk" are what the scanner looks for.
- A skill-category label is itself indexed, so make the labels carry keywords:
  `Vendor Management` beats `Vendor and SaaS Lifecycle`.
- Say years of experience **in digits**: "9+ years", never "nine years".
- No keyword more than three times. Stuffing scores worse than natural placement.

Only claim what the selected track files support. This is about wording what is already
true in the language the scanner expects, never about adding claims.

## Cover letter voice

First person, active voice, same bans as above. Every claim, project and metric must
already appear in the resume. 250 to 400 words. A letter generic enough to send unmodified
to another company has failed the step.

---

# Step 9: Answering quiz questions

Application forms ask ten or twenty short-answer questions, and pasting that many into a
terminal is miserable, so the questions come from `input/quiz-{slug}.txt` rather than chat.

## Parsing the file

The file is free-form and hand-written, so accept whatever shape it is in: numbered lines,
bullets, blank-line separated blocks, one question per line. A question mark is a hint, not
a requirement, since plenty of form fields read "Tell us why you want this role".

- Treat a block of several sentences as **one** question when it is clearly one form field
  with context around it. Splitting a single field into three answers is worse than merging
  two.
- Skip lines that are obviously not questions (a heading, a URL, the company name) silently.
- Re-read the file every time the user says yes; they may have added more. Skip any
  question already answered this session and say how many were skipped.
- If the user pastes questions inline instead, answer those in the same format. Do not
  demand the file.

## Output format

Emit the answers in file order, in exactly this shape. Nothing before it but a one-line
lead-in, nothing after it but the yes/no question again.

```
1. Question, copied or trimmed to one line

------------

Answer text.

------------

2. Next question

------------

Answer text.

------------
```

- The blank lines around each `------------` are **required.** Without them markdown turns
  the dashed line into a heading and the question or answer renders as a title.
- Twelve hyphens, on their own line, above and below every answer. Every answer is fenced
  on both sides, including the last.
- The answer sits alone between the dashes: no label, no "Answer:", no word count, no note
  about which resume bullet it came from. That block is what gets pasted into the form, so
  anything else in there is something the candidate deletes by hand.
- Commentary, caveats and anything needing a real answer from the user go **after the whole
  list**, never inside a fenced block.

## How the answers read

These are pasted into a form as the candidate's own words. A recruiter reads them next to
the resume, so they must not sound like the resume.

- **First person, plain spoken, written the way people actually talk.** Casual contractions
  are right: "I've", "it's", "didn't", "pretty much", "a bunch of", "honestly", "to be
  fair", "ended up". Ordinary US workplace slang is fine.
- **Short.** 2 to 4 sentences for a typical screening question, one sentence for a factual
  one. Longer only where the question asks for depth, and even then under a short paragraph.
- **No resume voice.** Do not paste or paraphrase resume bullets, do not lead with a strong
  verb and end with a percentage, do not stack three accomplishments into one sentence. If a
  sentence would fit under Professional Experience unchanged, rewrite it.
- **No AI register**, same ban list as above. Also out: "I am excited to", "I am passionate
  about", "aligns well with", "I would welcome the opportunity", opening by restating the
  question, and closing with a summary of what was just said.
- An imperfect sentence is fine. A little hedging is fine. It should read like someone typed
  it into a form in two minutes, not like it was drafted.

Ground rules that do not bend:

- **Every claim traces to the generated resume or a track file selected this run.** Casual
  wording is a style choice, not a licence to invent a project, a number or a job.
- If a question cannot be answered without fabricating, put the honest one-liner in the
  fenced block, then say plainly after the list what you need from the candidate. Typical
  cases: salary expectations, notice period, start date, visa or work authorisation,
  sponsorship, relocation, references, a GPA nobody recorded.
- Never guess at anything legal or contractual. Authorisation, clearance and sponsorship
  answers come from the candidate, always.
- If the user volunteers a real new fact here, offer to fold it into the track files per
  the sync rules in `logging.md`.

After the list, ask the yes/no question again, verbatim, as the last line. Loop until the
user says no. Nothing in this step touches `output/` or the two `data/` files.
