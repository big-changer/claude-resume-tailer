"""Render a resume (and its paired cover letter) from markdown to PDF.

The PDF is deliberately plain: one typeface, black text on white, a hairline
rule under each section heading, and nothing else. Colour, icon glyphs and
shaded tables all read as generated-by-a-tool, which is the opposite of the
goal here, so none of them are available.

Layout is structural, never textual. Blank lines and `---` rules in the source
markdown are ignored entirely -- spacing comes from the element being rendered,
so two runs of the generator produce the same rhythm regardless of how the
markdown happened to be spaced.

OUTPUT CONTRACT
---------------
The markdown this reads is not free-form. It must look like this:

    <!--
    target-company: Accuris
    target-role: SAP Solution Architect
    -->

    # Gafari Arowojebe
    SAP Solution Architect
    arowojebe.gafari.1127@gmail.com | +1 (224) 423-5835 | North Platte, NE
    linkedin.com/in/gafari-arowojebeg | github.com/codetechie-G

    ## Summary

    One or two short paragraphs.

    ## Technical Skills

    - **Systems and Linux**: Linux, TCP/IP, DNS, distributed systems
    - **Backend**: Python, Node.js, REST APIs, microservices

    ## Professional Experience

    ### Senior Backend Software Engineer | 02/2024 - 03/2026 | Las Vegas, NV
    #### NeoVegas Gaming Systems

    One line on what this role built and for whom.

    - One achievement per bullet.

    #### Key Projects

    - Project Name - what it does and what the candidate built in it.

    **Tech Stacks**: Python, FastAPI, PostgreSQL, React, Docker

    ## Education

    ### BSc. in Computer Science | 07/2012 - 05/2017 | St. Paul, MN
    #### University of St. Thomas

    Relevant Coursework: ...

    ## Certifications

    - Meta Back-End Developer Professional Certificate (Python, APIs)

`###` is `Title | dates | location`: the title sets bold on the left, the rest
sits grey and right-aligned on the same line. `####` directly under a `###` is
the company or school; anywhere else it is a sub-heading inside the entry, and
`Key Projects` is the only one the contract defines. Inline `**bold**` is
allowed on a skill label and on the `Tech Stacks` label, and nowhere else.

An experience entry is four parts in a fixed order: a one-line summary, the
achievement bullets, `#### Key Projects` with its projects, and the
`**Tech Stacks**:` line that closes it. verify_resume.py enforces that shape.

One application is one folder: the resume lives at
output/{YYYYMMDD}/{company}-{position}/{name}.md and its cover letter sits beside
it as {name}-cover-letter.md. Passing either the resume path or the folder
converts both, and the PDFs are written next to their markdown.

Every file is put through scripts/verify_resume.py first and no PDF is written
if a gate fails. Pass --no-verify to render anyway for a quick look.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, CondPageBreak, Frame, HRFlowable, KeepTogether, PageTemplate,
    Flowable, Paragraph, Spacer,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_resume as V  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / 'output'

# ── Page geometry ──────────────────────────────────────────────────────────
# The text frame carries no padding of its own. ReportLab's default frame adds
# 6pt on each side, which paragraphs respect and full-width tables do not, so
# the two drift apart: job titles and skill labels land 2.1mm left of the
# section heading above them, and right-aligned dates overhang the body text by
# the same amount. Zero padding makes MARGIN_X the single true text edge and
# AVAIL the exact usable width, so every element shares one left edge.
MARGIN_X = 16 * mm
MARGIN_Y = 13 * mm
AVAIL = letter[0] - 2 * MARGIN_X

# ── Palette — greyscale only, by design ────────────────────────────────────
# Kept dark for contrast. Light grey body text is a readability flag on resume
# checkers, so the lightest text here is still well above the usual threshold.
BLACK = HexColor('#000000')
BODY = HexColor('#1A1A1A')
GREY = HexColor('#3A3A3A')
RULE = HexColor('#7A7A7A')

# ── Type ───────────────────────────────────────────────────────────────────
# One family, sans-serif. Resume screeners consistently ask for a standard sans
# face (Arial, Helvetica, Open Sans, Roboto, Lato) rather than a serif, so Arial
# is used where it exists and Helvetica, a core PDF font that is metrically the
# same and needs no embedding, is the fallback. Never more than one family: a
# second face is a readability flag on every checker.
ROMAN, BOLD, ITALIC = 'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique'
_FONT_DIR = Path('C:/Windows/Fonts')
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    for _name, _file in (('Arial', 'arial.ttf'), ('Arial-Bold', 'arialbd.ttf'),
                         ('Arial-Italic', 'ariali.ttf')):
        pdfmetrics.registerFont(TTFont(_name, str(_FONT_DIR / _file)))
    pdfmetrics.registerFontFamily(
        'Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic')
    ROMAN, BOLD, ITALIC = 'Arial', 'Arial-Bold', 'Arial-Italic'
except Exception:
    pass   # Helvetica already set above

# ReportLab's canvas opens with Helvetica, which leaves it declared in every
# page's font resources even when nothing renders in it. Harmless to a parser
# that reads the drawn text, but a checker that counts declared fonts would see
# a third face, so the base font is pointed at the family actually in use.
from reportlab import rl_config  # noqa: E402

rl_config.canvas_basefontname = ROMAN

NAME_STYLE = ParagraphStyle(
    'Name', fontName=BOLD, fontSize=19, leading=23, textColor=BLACK, alignment=TA_CENTER)
HEADLINE_STYLE = ParagraphStyle(
    'Headline', fontName=BOLD, fontSize=11.5, leading=14, textColor=BLACK, alignment=TA_CENTER)
CONTACT_STYLE = ParagraphStyle(
    'Contact', fontName=ROMAN, fontSize=9.5, leading=12.6, textColor=GREY, alignment=TA_CENTER)
SECTION_STYLE = ParagraphStyle(
    'Section', fontName=BOLD, fontSize=11.5, leading=14, textColor=BLACK,
    spaceBefore=4 * mm)
BODY_STYLE = ParagraphStyle(
    'Body', fontName=ROMAN, fontSize=10, leading=13, textColor=BODY,
    alignment=TA_JUSTIFY, spaceAfter=1.2 * mm)
BULLET_STYLE = ParagraphStyle(
    'Bullet', fontName=ROMAN, fontSize=10, leading=12.8, textColor=BODY,
    alignment=TA_JUSTIFY, leftIndent=4 * mm, bulletIndent=0, spaceAfter=0.9 * mm,
    # Without this the bullet marker silently falls back to Helvetica, which
    # embeds a second font face for the sake of one hyphen.
    bulletFontName=ROMAN, bulletFontSize=10)
# Cover letter. The resume styles are tuned for density; a letter is read top
# to bottom by one person, so it gets a slightly larger face, more leading and
# real paragraph spacing, and its address, subject and signature blocks keep
# their line breaks instead of being run together into one paragraph.
LETTER_META_STYLE = ParagraphStyle(
    'LetterMeta', fontName=ROMAN, fontSize=10.5, leading=14.5, textColor=BODY,
    alignment=TA_LEFT)
LETTER_SUBJECT_STYLE = ParagraphStyle(
    'LetterSubject', fontName=BOLD, fontSize=10.5, leading=14.5, textColor=BLACK,
    alignment=TA_LEFT)
LETTER_BODY_STYLE = ParagraphStyle(
    'LetterBody', fontName=ROMAN, fontSize=10.5, leading=14.5, textColor=BODY,
    alignment=TA_JUSTIFY, spaceAfter=3.2 * mm)
LETTER_SIGNATURE_STYLE = ParagraphStyle(
    'LetterSignature', fontName=BOLD, fontSize=10.5, leading=14.5, textColor=BLACK,
    alignment=TA_LEFT)
LETTER_HEADER_GAP = 6 * mm      # rule under the contact block to the date
LETTER_BLOCK_GAP = 4.5 * mm     # between date, address, subject and salutation
LETTER_SIGNATURE_GAP = 9 * mm   # room for a handwritten signature
# The last block of the letter is the sign-off when it opens with one of these.
LETTER_CLOSINGS = ('sincerely', 'regards', 'best', 'kind', 'warm', 'yours',
                   'respectfully', 'thank you')

# Job or degree title, company or school, and dates/location are rendered by a
# custom flowable so the entry uses the full frame width without introducing a
# PDF table. Tables make some resume parsers read the right column out of order.
ENTRY_TITLE_STYLE = ParagraphStyle(
    'EntryTitle', fontName=BOLD, fontSize=10.5, leading=13.2, textColor=BLACK,
    alignment=TA_LEFT)
ENTRY_SUB_STYLE = ParagraphStyle(
    'EntrySub', fontName=ITALIC, fontSize=10, leading=13, textColor=GREY,
    alignment=TA_LEFT)
# A `####` line that is not the company under a job title is a sub-heading
# inside the entry, and "Key Projects" is the only one the contract defines.
# Drawn bold and black rather than italic grey, because it introduces content
# instead of naming the employer the reader has already seen.
SUBHEAD_STYLE = ParagraphStyle(
    'Subhead', fontName=BOLD, fontSize=10, leading=13, textColor=BLACK,
    alignment=TA_LEFT, spaceBefore=1.2 * mm, spaceAfter=1.0 * mm)
# Technical skills are laid out as two aligned columns: the bold category on
# the left, its skills on the right. The category column is sized once for the
# whole section so every row shares one boundary, which is what makes the block
# read as a table rather than as a run of wrapped sentences.
#
# This was briefly a single hanging-indented paragraph per row, which lost the
# bold on the category (the row regex strips the asterisks before the label
# reaches the renderer, so inline() had nothing to embolden) and ran the label
# into its values. The two-column form is back because that is the shape the
# candidate signs off on; it still draws label-then-values in reading order,
# so a text extractor sees the category immediately followed by its skills.
SKILL_LABEL_STYLE = ParagraphStyle(
    'SkillLabel', fontName=BOLD, fontSize=10, leading=13, textColor=BLACK,
    alignment=TA_LEFT)
SKILL_VALUE_STYLE = ParagraphStyle(
    'SkillValue', fontName=ROMAN, fontSize=10, leading=13, textColor=BODY,
    alignment=TA_LEFT)
SKILL_GUTTER = 4 * mm
SKILL_ROW_GAP = 1.6 * mm
# Bounds on the category column. Too narrow and long categories wrap to three
# lines beside a two-line value; too wide and the skills column is squeezed.
SKILL_LABEL_MIN = 0.20
SKILL_LABEL_MAX = 0.32

# No PDF tables anywhere in this renderer, by design. Every flowable draws its
# text in reading order, so that is the order the extracted text comes out in.


# ── Inline markdown ────────────────────────────────────────────────────────
def escape_xml(text: str) -> str:
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# Autolinking. The visible text is never rewritten, only wrapped, so an ATS
# still reads "linkedin.com/in/gafari-arowojebeg" as plain text while a human
# reader gets a working link. Underline is the only affordance: a blue link
# would put colour back into a deliberately greyscale document.
EMAIL_RE = re.compile(r'\b[\w.+-]+@[\w-]+\.[\w.-]*\w\b')
URL_RE = re.compile(
    r'\b(?:https?://|www\.)\S+?(?=[.,;:)\]]?(?:\s|$))'
    r'|\b(?:[\w-]+\.)+(?:com|org|net|io|dev|co|me|ai|app|xyz|edu|gov)'
    r'(?:/[^\s|]*)?'
)


def _anchor(href: str, label: str) -> str:
    return f'<a href="{href}"><u>{label}</u></a>'


def autolink(escaped: str) -> str:
    """Wrap bare emails and URLs in link annotations. Input must be XML-escaped."""
    def email(m):
        return _anchor(f'mailto:{m.group(0)}', m.group(0))

    def url(m):
        raw = m.group(0)
        has_scheme = raw.lower().startswith(('http://', 'https://', 'www.'))
        # A bare "word.tld" match with no scheme is only trusted as a URL when
        # its host portion is lower case, as a real domain always is written
        # (linkedin.com, github.com). A path or username after the slash, such
        # as GitHub's "codetechie-G", may still be mixed case. This is what
        # tells "github.com/codetechie-G" apart from a mixed-case technology
        # name that happens to end in a TLD word, like "ASP.NET".
        if not has_scheme:
            host = raw.split('/', 1)[0]
            if host != host.lower():
                return raw
        href = raw if has_scheme else f'https://{raw}'
        return _anchor(href, raw)

    # Emails first: an address contains a domain the URL pattern would match.
    parts, last = [], 0
    for m in EMAIL_RE.finditer(escaped):
        parts.append(URL_RE.sub(url, escaped[last:m.start()]))
        parts.append(email(m))
        last = m.end()
    parts.append(URL_RE.sub(url, escaped[last:]))
    return ''.join(parts)


def inline(text: str, link: bool = True) -> str:
    """Markdown emphasis to ReportLab's inline markup, with URLs made clickable."""
    text = escape_xml(text)
    if link:
        text = autolink(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
    return text


# ── Flowable builders ──────────────────────────────────────────────────────
# A heading stranded at the foot of a page with its content overleaf is the one
# layout fault the flow model will happily produce on its own. Both headings
# demand enough room for a first line or two of what they introduce.
SECTION_ORPHAN_GUARD = 22 * mm
ENTRY_ORPHAN_GUARD = 26 * mm


def section_heading(title: str) -> list:
    """Heading plus its hairline rule, kept on one page together."""
    return [
        CondPageBreak(SECTION_ORPHAN_GUARD),
        KeepTogether([
            Paragraph(escape_xml(title).upper(), SECTION_STYLE),
            HRFlowable(width='100%', thickness=0.4, color=RULE,
                       spaceBefore=0.8 * mm, spaceAfter=2.4 * mm),
        ]),
    ]


class EntryHeading(Flowable):
    """Full-width job or education heading without a PDF table."""

    def __init__(self, title: str, meta_parts: list[str], subtitle: str):
        super().__init__()
        self.title = title
        self.meta = ' | '.join(p for p in meta_parts if p)
        self.subtitle = subtitle
        self._width = AVAIL
        self._height = 0
        self._title_lines: list[str] = []
        self._subtitle_lines: list[str] = []

    @staticmethod
    def _fit_lines(text: str, font: str, size: float, max_width: float) -> list[str]:
        words = text.split()
        if not words:
            return []
        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f'{current} {word}'
            if stringWidth(candidate, font, size) <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def wrap(self, availWidth, availHeight):
        self._width = availWidth
        title_size = ENTRY_TITLE_STYLE.fontSize
        meta_size = ENTRY_SUB_STYLE.fontSize
        meta_width = stringWidth(self.meta, ROMAN, meta_size) if self.meta else 0
        gutter = 6 * mm if self.meta else 0
        sub_width = max(availWidth - meta_width - gutter, availWidth * 0.45)

        self._title_lines = self._fit_lines(self.title, BOLD, title_size, availWidth)
        self._subtitle_lines = self._fit_lines(self.subtitle, ITALIC, meta_size, sub_width)
        title_height = max(1, len(self._title_lines)) * ENTRY_TITLE_STYLE.leading
        sub_height = max(1, len(self._subtitle_lines)) * ENTRY_SUB_STYLE.leading if self.subtitle or self.meta else 0
        self._height = title_height + sub_height + 0.6 * mm
        return availWidth, self._height

    def draw(self):
        c = self.canv
        y = self._height - ENTRY_TITLE_STYLE.fontSize

        c.setFillColor(BLACK)
        c.setFont(BOLD, ENTRY_TITLE_STYLE.fontSize)
        for line in self._title_lines:
            c.drawString(0, y, line)
            y -= ENTRY_TITLE_STYLE.leading

        sub_y = y + 0.8 * mm
        if self.subtitle:
            c.setFillColor(GREY)
            c.setFont(ITALIC, ENTRY_SUB_STYLE.fontSize)
            for line in self._subtitle_lines:
                c.drawString(0, sub_y, line)
                sub_y -= ENTRY_SUB_STYLE.leading

        if self.meta:
            c.setFillColor(GREY)
            c.setFont(ROMAN, ENTRY_SUB_STYLE.fontSize)
            c.drawRightString(self._width, y + 0.8 * mm, self.meta)


def entry_heading(title: str, meta_parts: list[str], subtitle: str) -> list:
    """Job or degree heading spanning the full frame width."""
    return [CondPageBreak(ENTRY_ORPHAN_GUARD), Spacer(1, 0.9 * mm), KeepTogether([
        EntryHeading(title, meta_parts, subtitle),
    ])]


class SkillRow(Flowable):
    """One category and its skills, drawn as two aligned columns.

    Still not a PDF table. The two columns are two paragraphs placed by hand,
    and the label is drawn before its values, so the extracted text stays in
    reading order -- "Databases" immediately followed by the skills that belong
    to it -- which is what a keyword scanner reads. A real table would let a
    parser walk the right column on its own and detach the skills from their
    category. The label arrives without its markdown asterisks (the row regex
    strips them), so its weight comes from SKILL_LABEL_STYLE, not from inline().
    """

    def __init__(self, label: str, value: str, label_width: float):
        super().__init__()
        self.label_para = Paragraph(inline(label, link=False), SKILL_LABEL_STYLE)
        self.value_para = Paragraph(inline(value), SKILL_VALUE_STYLE)
        self.label_width = label_width
        self._width = AVAIL
        self._label_height = 0.0
        self._value_height = 0.0
        self._label_width_used = label_width

    def wrap(self, availWidth, availHeight):
        self._width = availWidth
        label_w = min(self.label_width, availWidth * SKILL_LABEL_MAX)
        value_w = availWidth - label_w - SKILL_GUTTER
        _, self._label_height = self.label_para.wrap(label_w, availHeight)
        _, self._value_height = self.value_para.wrap(value_w, availHeight)
        self._label_width_used = label_w
        return availWidth, max(self._label_height, self._value_height)

    def draw(self):
        height = max(self._label_height, self._value_height)
        # Both columns hang from the same top edge, so the category sits level
        # with the first line of its skills however far the skills wrap.
        self.label_para.drawOn(self.canv, 0, height - self._label_height)
        self.value_para.drawOn(
            self.canv, self._label_width_used + SKILL_GUTTER,
            height - self._value_height)


def skill_column_width(rows: list[tuple[str, str]]) -> float:
    """Width of the category column: the widest category, within bounds."""
    widest = max(
        (stringWidth(label, BOLD, SKILL_LABEL_STYLE.fontSize) for label, _ in rows),
        default=0)
    return max(min(widest + SKILL_GUTTER, AVAIL * SKILL_LABEL_MAX),
               AVAIL * SKILL_LABEL_MIN)


def skill_block(rows: list[tuple[str, str]]) -> list:
    """The whole technical skills block, every row sharing one column boundary."""
    label_width = skill_column_width(rows)
    block: list = []
    for index, (label, value) in enumerate(rows):
        if index:
            block.append(Spacer(1, SKILL_ROW_GAP))
        block.append(SkillRow(label, value, label_width))
    return block


# ── Markdown to flowables ──────────────────────────────────────────────────
def build_story(text: str) -> list:
    doc = V.Doc(text)
    lines = doc.body.splitlines()
    story: list = []

    pending_skills: list[tuple[str, str]] = []
    paragraph: list[str] = []
    section = ''

    def flush_paragraph():
        if paragraph:
            story.append(Paragraph(inline(' '.join(paragraph)), BODY_STYLE))
            paragraph.clear()

    def flush_skills():
        if pending_skills:
            story.extend(skill_block(pending_skills))
            story.append(Spacer(1, 0.6 * mm))
            pending_skills.clear()

    def flush_all():
        flush_paragraph()
        flush_skills()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Header block: name, then headline, then contact lines.
        if line.startswith('# '):
            flush_all()
            story.append(Paragraph(escape_xml(line[2:].strip()), NAME_STYLE))
            i += 1
            first = True
            while i < len(lines) and lines[i].strip():
                value = lines[i].strip()
                if first:
                    story.append(Spacer(1, 1.2 * mm))
                    story.append(Paragraph(inline(value), HEADLINE_STYLE))
                    story.append(Spacer(1, 1.6 * mm))
                    first = False
                else:
                    # Autolinked like the body: the email and the profile
                    # URLs stay the bare strings a parser reads, and the
                    # annotation on top makes them clickable for a human.
                    story.append(Paragraph(inline(value), CONTACT_STYLE))
                i += 1
            story.append(Spacer(1, 1.4 * mm))
            continue

        if not line or line == '---':
            flush_paragraph()
            i += 1
            continue

        m = V.SECTION_RE.match(line)
        if m:
            flush_all()
            section = m.group(1).strip().upper()
            story.extend(section_heading(m.group(1).strip()))
            i += 1
            continue

        m = V.ENTRY_RE.match(line)
        if m:
            flush_all()
            parts = [p.strip() for p in m.group(1).split('|')]
            subtitle = ''
            if i + 1 < len(lines):
                sm = V.SUBENTRY_RE.match(lines[i + 1].strip())
                if sm:
                    subtitle = sm.group(1).strip()
                    i += 1
            story.extend(entry_heading(parts[0], parts[1:], subtitle))
            i += 1
            continue

        m = V.SUBENTRY_RE.match(line)   # a #### that is not a company line
        if m:
            flush_all()
            story.append(Paragraph(escape_xml(m.group(1).strip()), SUBHEAD_STYLE))
            i += 1
            continue

        m = V.SKILL_ROW_RE.match(line)
        if m and section == 'TECHNICAL SKILLS':
            flush_paragraph()
            pending_skills.append((m.group(1).strip(), m.group(2).strip()))
            i += 1
            continue

        if line.startswith('- '):
            flush_all()
            story.append(Paragraph(inline(line[2:].strip()), BULLET_STYLE, bulletText='-'))
            i += 1
            continue

        flush_skills()
        paragraph.append(line)
        i += 1

    flush_all()
    return story


def build_letter_story(text: str, header_from: str | None = None) -> list:
    """A business-letter layout for the cover letter.

    The markdown is the same shape the resume uses (name, headline, contact,
    then paragraphs separated by blank lines), and the blocks are told apart
    by position and shape rather than by any markup, so the skill writes the
    letter exactly as before:

        date                    first block
        address                 every block up to the salutation, line breaks kept
        Re: role - company      generated from the metadata comment
        Dear ...,               the salutation, a single line ending in a comma
        body paragraphs         everything else, justified
        Sincerely, / name       the last block, with room for a signature

    `header_from` is the paired resume's markdown. The contract has the letter
    carry its own header block and the verifier now blocks one that does not,
    but a letter rendered with --no-verify, or one written before that gate
    existed, still gets a letterhead: the resume's, since the two are one
    application.
    """
    doc = V.Doc(text)
    lines = doc.body.splitlines()
    story: list = []

    header = doc
    if not doc.name and header_from:
        header = V.Doc(header_from)

    # Letterhead, as on the resume, closed by a hairline so the letter proper
    # has a clear top edge.
    if header.name:
        story.append(Paragraph(escape_xml(header.name), NAME_STYLE))
        if header.headline:
            story.append(Spacer(1, 1.2 * mm))
            story.append(Paragraph(inline(header.headline), HEADLINE_STYLE))
            story.append(Spacer(1, 1.6 * mm))
        for value in header.contact:
            story.append(Paragraph(inline(value), CONTACT_STYLE))
        story.append(HRFlowable(width='100%', thickness=0.4, color=RULE,
                                spaceBefore=2.4 * mm, spaceAfter=LETTER_HEADER_GAP))

    # Everything after the header block, grouped into blank-line-separated
    # blocks. With no header in this file, the letter starts at the top.
    i = 0
    if doc.name:
        while i < len(lines) and not lines[i].strip().startswith('# '):
            i += 1
        while i < len(lines) and lines[i].strip():
            i += 1
    blocks: list[list[str]] = []
    current: list[str] = []
    for raw in lines[i:]:
        line = raw.strip()
        if line and line != '---':
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    if not blocks:
        return story

    def is_salutation(block: list[str]) -> bool:
        return len(block) == 1 and block[0].endswith(',') and block[0].lower().startswith('dear')

    def is_closing(block: list[str]) -> bool:
        return block[0].lower().rstrip(',').startswith(LETTER_CLOSINGS)

    def lines_para(block: list[str], style: ParagraphStyle) -> Paragraph:
        return Paragraph('<br/>'.join(inline(l) for l in block), style)

    # "Sincerely," and the name are one block whether the writer left a blank
    # line between them or not.
    if (len(blocks) > 2 and len(blocks[-2]) == 1 and is_closing(blocks[-2])
            and len(blocks[-1]) <= 2 and not is_closing(blocks[-1])):
        blocks[-2:] = [blocks[-2] + blocks[-1]]

    salutation_at = next((k for k, b in enumerate(blocks) if is_salutation(b)), None)
    closing_at = len(blocks) - 1 if len(blocks) > 1 and is_closing(blocks[-1]) else None

    # Date and address: the blocks before the salutation, each on its own lines.
    head_end = salutation_at if salutation_at is not None else 0
    for block in blocks[:head_end]:
        story.append(lines_para(block, LETTER_META_STYLE))
        story.append(Spacer(1, LETTER_BLOCK_GAP))

    # Subject line from the metadata the skill already writes.
    role = doc.meta.get('target-role', '').strip()
    company = doc.meta.get('target-company', '').strip()
    if role or company:
        subject = ' - '.join(p for p in (role, company) if p)
        story.append(Paragraph(f'Re: {escape_xml(subject)}', LETTER_SUBJECT_STYLE))
        story.append(Spacer(1, LETTER_BLOCK_GAP))

    if salutation_at is not None:
        story.append(lines_para(blocks[salutation_at], LETTER_META_STYLE))
        story.append(Spacer(1, LETTER_BLOCK_GAP * 0.7))

    body_start = head_end + (1 if salutation_at is not None else 0)
    body_end = closing_at if closing_at is not None else len(blocks)
    for block in blocks[body_start:body_end]:
        story.append(Paragraph(inline(' '.join(block)), LETTER_BODY_STYLE))

    # Sign-off: the closing phrase, a gap for the signature, then the name in
    # bold. Any further lines (a phone number, say) follow the name.
    if closing_at is not None:
        closing = blocks[closing_at]
        story.append(Spacer(1, LETTER_BLOCK_GAP * 0.4))
        story.append(Paragraph(inline(closing[0]), LETTER_META_STYLE))
        if len(closing) > 1:
            story.append(Spacer(1, LETTER_SIGNATURE_GAP))
            story.append(Paragraph(inline(closing[1]), LETTER_SIGNATURE_STYLE))
            for extra in closing[2:]:
                story.append(Paragraph(inline(extra), LETTER_META_STYLE))
    return story


# ── Rendering ──────────────────────────────────────────────────────────────
def render(md_path: Path, title: str) -> tuple[bytes, int]:
    """Build the PDF in memory. Returns its bytes and its page count."""
    buffer = io.BytesIO()
    doc = BaseDocTemplate(
        buffer, pagesize=letter,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_Y, bottomMargin=MARGIN_Y,
        title=title, author=title.split(' - ')[0],
    )
    frame = Frame(
        MARGIN_X, MARGIN_Y, AVAIL, letter[1] - 2 * MARGIN_Y,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id='body',
    )
    doc.addPageTemplates([PageTemplate(id='page', frames=[frame])])
    text = md_path.read_text(encoding='utf-8')
    if V.is_cover_file(md_path):
        resume_md = md_path.with_name(
            md_path.stem[:-len(V.COVER_SUFFIX)] + md_path.suffix)
        header_from = (resume_md.read_text(encoding='utf-8')
                       if resume_md.exists() else None)
        story = build_letter_story(text, header_from)
    else:
        story = build_story(text)
    doc.build(story)
    return buffer.getvalue(), doc.page


def resolve_md_path(raw_arg: str) -> Path:
    """Validate a CLI argument and resolve it to an absolute .md path inside output/."""
    arg_path = Path(raw_arg)
    if arg_path.is_absolute() or '..' in arg_path.parts:
        raise ValueError('Pass only a relative path inside the output/ directory.')

    md_path = (OUTPUT_DIR / arg_path).resolve()
    if md_path.is_dir():
        # An application folder, output/{YYYYMMDD}/{company}-{position}/. It holds
        # one resume, its cover letter and the archived jd.md, so the resume is
        # the only sensible target and the cover letter is picked up alongside it
        # as usual.
        resumes = [p for p in sorted(md_path.glob('*.md'))
                   if not V.is_cover_file(p) and not V.is_jd_archive(p)]
        if len(resumes) != 1:
            raise ValueError(
                f'{raw_arg} holds {len(resumes)} resume markdown files; name the one to convert.')
        md_path = resumes[0]
    elif md_path.suffix == '':
        md_path = md_path.with_suffix('.md')
    elif md_path.suffix.lower() != '.md':
        raise ValueError(f'File must be a .md file: {arg_path}')

    if OUTPUT_DIR.resolve() not in md_path.parents:
        raise ValueError(f'File must be inside output/: {arg_path}')
    if V.is_jd_archive(md_path):
        raise ValueError(
            'jd.md is the archived job description, not a deliverable. '
            'Name the resume in that folder instead.')
    if not md_path.exists():
        raise FileNotFoundError(f'Markdown file not found: {md_path}')
    return md_path


def convert(md_path: Path, skip_verify: bool) -> bool:
    """Verify then write. Returns False if a gate blocked the write."""
    text = md_path.read_text(encoding='utf-8')
    is_cover = V.is_cover_file(md_path)

    gates = {} if skip_verify else V.verify(text, is_cover=is_cover)
    pdf_bytes, pages = render(md_path, md_path.stem)

    budget = V.MAX_PAGES_COVER if is_cover else V.MAX_PAGES_RESUME
    if not skip_verify and pages > budget:
        gates.setdefault('structure & length', []).append(
            f'renders to {pages} pages, over the {budget}-page budget'
        )

    if not skip_verify:
        if not V.report(md_path.name, gates):
            print(f'\n  BLOCKED, no PDF written: {md_path.name}')
            print('  Fix the items above and re-run, or pass --no-verify to render anyway.\n')
            return False
        print(f'  pages                {pages}')
        print()

    pdf_path = md_path.with_suffix('.pdf')
    try:
        pdf_path.write_bytes(pdf_bytes)
    except PermissionError:
        print(f'  Cannot write {pdf_path.name}: it is open in another program. '
              f'Close it and re-run.')
        return False
    print(f'Wrote {pdf_path}  ({pages} page{"s" if pages != 1 else ""})')
    return True


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    ap = argparse.ArgumentParser(
        description='Convert a resume markdown file (and its paired cover letter) to PDF.')
    ap.add_argument(
        'resume_md', nargs='+',
        help=("One or more paths relative to output/, e.g. "
              "'20260801/accuris-sap-solution-architect/gafari-arowojebe'. The .md "
              "extension is optional. A paired '<name>-cover-letter.md' in the same "
              "directory is converted automatically."))
    ap.add_argument(
        '--no-verify', action='store_true',
        help='render without running the quality gates (for a quick look only)')
    args = ap.parse_args()

    converted: set[Path] = set()
    ok = True

    for raw_arg in args.resume_md:
        md_path = resolve_md_path(raw_arg)
        if md_path in converted:
            continue
        ok &= convert(md_path, args.no_verify)
        converted.add(md_path)

        if not V.is_cover_file(md_path):
            cover_path = V.cover_path_for(md_path)
            if cover_path.exists() and cover_path not in converted:
                ok &= convert(cover_path, args.no_verify)
                converted.add(cover_path)

    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
