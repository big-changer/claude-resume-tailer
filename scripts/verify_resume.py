"""Blocking quality gates for generated resume / cover-letter markdown.

Every gate here exists because a specific defect shipped in a real output file.
The gates are executable on purpose: a prose checklist that the generating model
ticks off itself does not stop the same defect recurring on the next run.

  Gate 1  human style    no AI-tell symbols, no AI-tell phrasing, no bracketed
                         placeholders left in the deliverable
  Gate 2  frozen facts   every company, date, location, school and contact value
                         in the output is verified to exist in one of the
                         input/master-resume-{track}.md files, which together are
                         the source of truth
  Gate 3  headline       the role under the name tracks the target job title and
                         is not left over from the master resume
  Gate 4  emphasis       no inline bold outside the one structural position that
                         allows it (technical-skill category labels)
  Gate 5  structure      the file matches the output contract, and is short
                         enough to land inside its page budget

Used as a library by convert_resume.py (which refuses to write a PDF when any
gate fails) and runnable on its own:

    python scripts/verify_resume.py 20260801/accuris-sap-solution-architect
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# There is no combined master resume. Each input/master-resume-{track}.md is the
# whole record filtered to one kind of role, and each carries the same facts, so
# the gate checks the union of them. master-resume-bone.md is excluded: it is the
# anonymised sharing template, and its bracketed placeholders are not facts.
MASTER_DIR = ROOT / 'input'
MASTER_GLOB = 'master-resume-*.md'
MASTER_EXCLUDE = {'master-resume-bone.md'}


def master_resumes(directory: Path = MASTER_DIR) -> list[Path]:
    """Every track file the frozen-facts gate treats as a source of truth."""
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.glob(MASTER_GLOB) if p.name not in MASTER_EXCLUDE
    )

# Budgets. The reference two-page resume this pipeline is modelled on runs about
# 900 words; the cover-letter budget matches the 250-400 word rule in the skill.
MAX_WORDS_RESUME = 1050
MAX_WORDS_COVER = 430
MAX_PAGES_RESUME = 2
MAX_PAGES_COVER = 1


# ── Gate 1 — human-written style ───────────────────────────────────────────
BANNED_CHARS = {
    '—': 'em dash',
    '–': 'en dash',
    '…': 'ellipsis',
    '‘': 'curly quote',
    '’': 'curly quote',
    '“': 'curly quote',
    '”': 'curly quote',
    '•': 'bullet glyph',
    '▪': 'bullet glyph',
    '‣': 'bullet glyph',
    '●': 'bullet glyph',
    '◦': 'bullet glyph',
    '→': 'arrow',
    '⇒': 'arrow',
    '✓': 'checkmark',
    '✔': 'checkmark',
    '★': 'star',
    '➤': 'arrow',
    ' ': 'non-breaking space',
    '​': 'zero-width space',
    '﻿': 'byte order mark',
}

BANNED_PHRASES = [
    'leverag', 'delve', 'seamless', 'robust and scalable', 'spearhead',
    'cutting-edge', 'cutting edge', 'fast-paced world', 'showcas', 'underscor',
    "it's worth noting", 'not only', 'tapestry', 'pivotal', 'meticulous',
    'realm of', 'harness the power', "in today's", 'furthermore', 'moreover',
    'state-of-the-art', 'game-chang', 'unlock the', 'elevate the', 'myriad',
    'testament to', 'navigate the complex', 'synerg', 'at the forefront',
]

# A bracketed span is how every "to be supplied by candidate" placeholder and
# every [AI-Generated] marker reached the PDF. The contract has no legitimate
# use for square brackets, so all of them are rejected rather than pattern-matched.
BRACKET_RE = re.compile(r'\[[^\]\n]{0,120}\]')


def check_human_style(text: str) -> list[str]:
    problems = []
    for ch, label in sorted(BANNED_CHARS.items()):
        if ch in text:
            problems.append(f'AI-tell symbol: {label} (U+{ord(ch):04X})')

    low = text.lower()
    problems += [f'AI-tell phrase: {p!r}' for p in BANNED_PHRASES if p in low]

    for ch in set(text):
        if ord(ch) > 0x2100:
            problems.append(f'non-text glyph U+{ord(ch):04X} (emoji or pictograph)')

    for m in BRACKET_RE.finditer(text):
        problems.append(
            f'bracketed placeholder left in the deliverable: {m.group(0)!r} '
            f'(omit the entry instead, and report the gap in chat)'
        )
    return sorted(set(problems))


# ── Document model ─────────────────────────────────────────────────────────
COMMENT_RE = re.compile(r'<!--(.*?)-->', re.DOTALL)
ENTRY_RE = re.compile(r'^###\s+(.*)$')
SUBENTRY_RE = re.compile(r'^####\s+(.*)$')
SECTION_RE = re.compile(r'^##\s+(.*)$')
SKILL_ROW_RE = re.compile(r'^-\s+\*\*([^*]+)\*\*:\s*(.+)$')
DATE_RE = re.compile(r'\b(0[1-9]|1[0-2])/((?:19|20)\d{2})\b')

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june',
          'july', 'august', 'september', 'october', 'november', 'december']


class Doc:
    """The parsed shape of a resume markdown file, per the output contract."""

    def __init__(self, text: str, is_cover: bool = False):
        self.is_cover = is_cover
        self.meta = {}
        for block in COMMENT_RE.findall(text):
            for ln in block.splitlines():
                if ':' in ln:
                    k, _, v = ln.partition(':')
                    self.meta[k.strip().lower()] = v.strip()

        # Blank out the comment rather than deleting it, so the line numbers in
        # gate messages still point at the right line of the real file.
        self.body = COMMENT_RE.sub(lambda m: '\n' * m.group(0).count('\n'), text)
        lines = self.body.splitlines()

        self.name = ''
        self.headline = ''
        self.contact = []
        self.sections = {}      # upper-cased title -> list of raw lines
        self.entries = []       # (section, title, meta, subtitle)

        section = None
        i = 0
        while i < len(lines):
            raw = lines[i]
            line = raw.strip()

            if line.startswith('# ') and not self.name:
                self.name = line[2:].strip()
                j = i + 1
                while j < len(lines) and lines[j].strip():
                    if not self.headline:
                        self.headline = lines[j].strip()
                    else:
                        self.contact.append(lines[j].strip())
                    j += 1
                i = j
                continue

            m = SECTION_RE.match(line)
            if m:
                section = m.group(1).strip().upper()
                self.sections.setdefault(section, [])
                i += 1
                continue

            m = ENTRY_RE.match(line)
            if m:
                parts = [p.strip() for p in m.group(1).split('|')]
                title = parts[0]
                entry_meta = parts[1:]
                subtitle = ''
                if i + 1 < len(lines):
                    sm = SUBENTRY_RE.match(lines[i + 1].strip())
                    if sm:
                        subtitle = sm.group(1).strip()
                self.entries.append((section, title, entry_meta, subtitle))

            if section is not None:
                self.sections[section].append(raw)
            i += 1

        self.is_cover = self.is_cover or 'cover' in self.meta.get('kind', '').lower()


def _norm(s: str) -> str:
    """Fold away formatting noise: case, dash style, and all whitespace."""
    s = s.lower().replace('–', '-').replace('—', '-')
    return re.sub(r'\s+', '', s)


def _date_forms(token: str) -> list[str]:
    """Every spelling of an MM/YYYY date the master resume might use.

    The master resume writes dates as "July 2012" or "Jul 2012"; the output
    contract writes "07/2012". All three have to count as the same fact.
    """
    m = DATE_RE.fullmatch(token)
    if not m:
        return [_norm(token)]
    mm, yyyy = m.group(1), m.group(2)
    month = MONTHS[int(mm) - 1]
    return [_norm(f'{mm}/{yyyy}'), _norm(f'{month} {yyyy}'), _norm(f'{month[:3]} {yyyy}')]


# ── Gate 2 — frozen facts, verified against the track files ────────────────
def check_frozen(doc: Doc, sources: list[Path] | None = None) -> list[str]:
    """Every hard fact in the output must already exist in a track file.

    Checked in that direction on purpose. Listing the facts here instead would
    mean a typo in this file could quietly become the new truth.

    The union of the track files is the widest thing that can be checked here,
    because this gate does not know which tracks the run selected. Keeping the
    output's facts to the *primary* track specifically is a rule in the skill,
    not something this gate can enforce.
    """
    sources = master_resumes() if sources is None else sources
    if not sources:
        return [
            f'no track files matching {MASTER_GLOB} in {MASTER_DIR}, '
            f'cannot verify frozen facts'
        ]

    # Joined with a NUL, which _norm leaves alone, so one file's trailing text
    # and the next one's leading text cannot form a spurious match across the
    # boundary.
    master = '\x00'.join(
        _norm(p.read_text(encoding='utf-8')) for p in sources
    )
    problems = []

    def require(value: str, what: str):
        if not value:
            return
        if not any(f in master for f in _date_forms(value)):
            problems.append(f'{what} not found in any track file: {value!r}')

    # Contact block: only the machine-checkable values. A location is written
    # differently on a resume than in the master file ("North Platte, NE, USA
    # (Remote)" vs a structured address), so it is not compared literally.
    for seg in (s.strip() for line in doc.contact for s in line.split('|')):
        if re.fullmatch(r'[\w.+-]+@[\w.-]+\.\w+', seg):
            require(seg, 'email')
        elif re.fullmatch(r'\+?[\d][\d\s().-]{5,}', seg):
            require(seg, 'phone')
        elif 'linkedin.com' in seg.lower() or 'github.com' in seg.lower():
            require(seg, 'profile URL')

    for section, title, entry_meta, subtitle in doc.entries:
        if section not in ('PROFESSIONAL EXPERIENCE', 'EDUCATION'):
            continue
        what = 'company' if section == 'PROFESSIONAL EXPERIENCE' else 'institution'
        require(subtitle, what)
        for chunk in entry_meta:
            for token in DATE_RE.findall(chunk):
                require(f'{token[0]}/{token[1]}', 'date')
            location = chunk.strip()
            if not DATE_RE.search(location) and ',' in location:
                require(location, 'location')

    return problems


# ── Gate 3 — the headline must track the target job title ──────────────────
MASTER_HEADLINE = 'Full Stack Developer'

GENERIC_TITLE_WORDS = {
    'senior', 'sr', 'junior', 'jr', 'lead', 'staff', 'principal', 'developer',
    'engineer', 'specialist', 'consultant', 'architect', 'programmer', 'analyst',
    'manager', 'i', 'ii', 'iii', 'iv', 'level', 'and', 'or', 'of', 'the',
}


def _title_tokens(s: str) -> set[str]:
    return {t for t in re.split(r'[^a-z0-9+#.]+', s.lower()) if t}


def check_headline(doc: Doc) -> list[str]:
    headline = doc.headline.strip()
    role = doc.meta.get('target-role', '').strip()

    if not headline:
        return ['the line under the name is empty, so the role would render blank']
    if not role:
        return [
            'no `target-role` in the metadata comment, so the headline cannot be '
            'verified against the job description'
        ]

    if '|' in headline:
        return [
            f'headline {headline!r} is a multi-part title. Use the job title on '
            f'its own, with no pipes and no technology list.'
        ]
    if len(headline) > 60:
        return [f'headline is {len(headline)} chars, over the 60-char single-line budget']

    h_all, r_all = _title_tokens(headline), _title_tokens(role)
    r_key = r_all - GENERIC_TITLE_WORDS
    missing = sorted((r_key or r_all) - h_all)
    if missing:
        return [
            f'headline {headline!r} does not match target role {role!r} '
            f'(missing {", ".join(missing)})'
        ]
    if _norm(headline) == _norm(MASTER_HEADLINE) and _norm(role) != _norm(MASTER_HEADLINE):
        return [f'headline is still the master-resume default {MASTER_HEADLINE!r}']
    if not (h_all - GENERIC_TITLE_WORDS) and r_key:
        return [f'headline {headline!r} is all generic words, so nothing was retargeted']
    return []


# ── Gate 4 — emphasis budget ───────────────────────────────────────────────
def check_emphasis(doc: Doc) -> list[str]:
    """Inline bold is allowed in exactly one place: a technical-skill label.

    Bold buys nothing at the ATS layer, which reads the plain text either way.
    It only spends the reader's attention, so it is spent on structure.
    """
    problems = []
    for n, raw in enumerate(doc.body.splitlines(), 1):
        line = raw.strip()
        if not line or SKILL_ROW_RE.match(line):
            continue
        if '**' in line:
            snippet = line if len(line) <= 70 else line[:67] + '...'
            problems.append(f'line {n}: inline bold outside a skill label: {snippet}')
    if len(problems) > 6:
        head = problems[:6]
        head.append(f'... and {len(problems) - 6} more bolded lines')
        return head
    return problems


# ── Gate 5 — structure and length ──────────────────────────────────────────
REQUIRED_SECTIONS = ['SUMMARY', 'TECHNICAL SKILLS', 'PROFESSIONAL EXPERIENCE', 'EDUCATION']
BANNED_SECTIONS = {
    'CORE COMPETENCIES': 'duplicates TECHNICAL SKILLS; keep one skills section',
    'KEY SKILLS': 'duplicates TECHNICAL SKILLS; keep one skills section',
    'CORE SKILLS': 'duplicates TECHNICAL SKILLS; keep one skills section',
    'LEADERSHIP & IMPACT': 'fold into the experience bullets it restates',
    'LEADERSHIP AND IMPACT': 'fold into the experience bullets it restates',
    'GAP ANALYSIS': 'report gaps in chat, not in the deliverable',
}
MAX_SKILL_ROWS = 8
# Skill labels share one column, sized to the widest of them. A single long
# label therefore pushes every value on the page to the right and leaves the
# short labels sitting in a void, so label length is a layout constraint rather
# than a style preference.
MAX_SKILL_LABEL_CHARS = 26


def check_structure(doc: Doc) -> list[str]:
    problems = []
    words = len(doc.body.split())

    if doc.is_cover:
        if words > MAX_WORDS_COVER:
            problems.append(f'cover letter is {words} words, over the {MAX_WORDS_COVER}-word budget')
        return problems

    if not doc.name:
        problems.append('no `# Name` heading found')

    for want in REQUIRED_SECTIONS:
        if want not in doc.sections:
            problems.append(f'missing required section: {want}')

    for got, why in BANNED_SECTIONS.items():
        if got in doc.sections:
            problems.append(f'section {got} should not exist: {why}')

    if '|' in doc.body and re.search(r'^\s*\|.*\|\s*$', doc.body, re.MULTILINE):
        problems.append('markdown table found; the contract uses skill rows, not tables')

    rows = [ln for ln in doc.sections.get('TECHNICAL SKILLS', []) if SKILL_ROW_RE.match(ln.strip())]
    if 'TECHNICAL SKILLS' in doc.sections and not rows:
        problems.append('TECHNICAL SKILLS has no `- **Label**: values` rows')
    if len(rows) > MAX_SKILL_ROWS:
        problems.append(
            f'TECHNICAL SKILLS has {len(rows)} categories, over the {MAX_SKILL_ROWS} '
            f'budget. Cut the ones the job description does not ask for.'
        )
    for ln in rows:
        label = SKILL_ROW_RE.match(ln.strip()).group(1).strip()
        if len(label) > MAX_SKILL_LABEL_CHARS:
            problems.append(
                f'skill label {label!r} is {len(label)} chars, over the '
                f'{MAX_SKILL_LABEL_CHARS}-char budget. It widens the label column for '
                f'every row, so shorten it.'
            )

    for section, title, entry_meta, subtitle in doc.entries:
        if section in ('PROFESSIONAL EXPERIENCE', 'EDUCATION'):
            if not entry_meta:
                problems.append(f'entry {title!r} has no `| dates | location` on its heading line')
            if not subtitle:
                problems.append(f'entry {title!r} has no `#### Company` line under it')

    if words > MAX_WORDS_RESUME:
        problems.append(
            f'resume is {words} words, over the {MAX_WORDS_RESUME}-word budget for two pages'
        )
    return problems


# ── Driver ─────────────────────────────────────────────────────────────────
# ── Advisories — reported, never blocking ──────────────────────────────────
# Resume screeners look for around five quantified results. That target cannot
# be a gate: the only honest source of a number is the master resume, so a gate
# would either block every build or push the generator into inventing figures.
# It is reported instead, for the candidate to close with real numbers.
TARGET_METRICS = 5
METRIC_RE = re.compile(
    r'\d+\s*(?:%|percent)|\$\s*\d|\d+\s*(?:x|hours?|days?|weeks?|months?|users?|'
    r'systems?|apps?|applications?|teams?|people|engineers?)\b|\b\d+\+\s*years?',
    re.IGNORECASE,
)


def advise(doc: Doc) -> list[str]:
    if doc.is_cover:
        return []
    notes = []
    hits = {m.group(0).strip() for ln in doc.body.splitlines()
            if ln.strip().startswith('- ') or not ln.startswith('#')
            for m in METRIC_RE.finditer(ln)}
    hits = {h for h in hits if not DATE_RE.fullmatch(h)}
    if len(hits) < TARGET_METRICS:
        notes.append(
            f'{len(hits)} measurable result(s) found ({", ".join(sorted(hits)) or "none"}); '
            f'screeners look for about {TARGET_METRICS}. Only add more if the master '
            f'resume has real numbers to draw on, and otherwise report the shortfall.'
        )
    return notes


def verify(text: str, is_cover: bool = False) -> dict[str, list[str]]:
    """Run every gate. Returns gate name -> problems (empty list means pass)."""
    doc = Doc(text, is_cover=is_cover)
    gates = {
        'human style': check_human_style(doc.body),
        'frozen facts': check_frozen(doc),
        'emphasis budget': check_emphasis(doc),
        'structure & length': check_structure(doc),
    }
    # A cover letter has no headline of its own to retarget.
    gates['headline'] = [] if doc.is_cover else check_headline(doc)
    verify.last_advisories = advise(doc)
    return gates


def report(name: str, gates: dict[str, list[str]]) -> bool:
    """Print a gate report. Returns True when everything passed."""
    print('=' * 66)
    print(f'  VERIFY  {name}')
    print('=' * 66)
    ok = True
    for gate, problems in gates.items():
        print(f'  {gate:<20} {"PASS" if not problems else "FAIL"}')
        for p in problems:
            print(f'      ! {p}')
        ok = ok and not problems
    for note in getattr(verify, 'last_advisories', []):
        print(f'  advisory             {note}')
    return ok


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('resume_md', nargs='+',
                    help='paths relative to output/, .md extension optional')
    args = ap.parse_args()

    failed = False
    for raw in args.resume_md:
        p = Path(raw)
        if p.suffix == '':
            p = p.with_suffix('.md')
        path = (ROOT / 'output' / p).resolve()
        if not path.exists():
            print(f'not found: {path}')
            failed = True
            continue
        gates = verify(path.read_text(encoding='utf-8'), is_cover=path.stem.endswith('-cover'))
        if not report(path.name, gates):
            failed = True
        print()
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
