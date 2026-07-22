from pathlib import Path
import argparse
import re

parser = argparse.ArgumentParser(
    description='Convert a resume markdown file to PDF.'
)
parser.add_argument(
    'resume_md',
    help=(
        'Path to a markdown file relative to the output/ directory, '
        "e.g. '20260722/cap-index-software-developer-evan-singleton-emphasize.md'. "
        'The .md extension is optional.'
    ),
)
args = parser.parse_args()

root = Path(__file__).resolve().parent.parent
output_dir = root / 'output'

resume_md = Path(args.resume_md)
print(resume_md)
if resume_md.is_absolute() or '..' in resume_md.parts:
    raise ValueError('Pass only a relative path inside the output/ directory, not a path.')
if resume_md.suffix == '':
    resume_md = resume_md.with_suffix('.md')
elif resume_md.suffix.lower() != '.md':
    raise ValueError(f'Resume file must be a .md file: {resume_md}')

md_path = (output_dir / resume_md).resolve()
if output_dir.resolve() not in md_path.parents:
    raise ValueError(f'Resume file must be inside output/: {resume_md}')
if not md_path.exists():
    raise FileNotFoundError(f'Resume markdown file not found: {md_path}')

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

docx_path = md_path.with_suffix('.docx')
pdf_path = md_path.with_suffix('.pdf')

# ── Fonts ──────────────────────────────────────────────────────────────────
# Arial supports Latvian characters (ē, ņ, š, etc.)
font_dir = Path('C:/Windows/Fonts')
try:
    pdfmetrics.registerFont(TTFont('Arial',           str(font_dir / 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Bold',      str(font_dir / 'arialbd.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Italic',    str(font_dir / 'ariali.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-BoldItalic',str(font_dir / 'arialbi.ttf')))
    pdfmetrics.registerFontFamily(
        'Arial',
        normal='Arial', bold='Arial-Bold',
        italic='Arial-Italic', boldItalic='Arial-BoldItalic',
    )
    F = 'Arial'
except Exception:
    F = 'Helvetica'   # fallback (limited Unicode)

# ── Icon font ──────────────────────────────────────────────────────────────
# Segoe UI Symbol has real outline glyphs for envelope/phone/pin/link (unlike
# Segoe UI Emoji, which is a colour font ReportLab can't render).
ICON_FONT = None
ICONS = {
    'email':    '✉',      # envelope
    'phone':    '☎',      # telephone
    'location': '\U0001F4CD',  # round pushpin
    'link':     '\U0001F517',  # link
}
icon_font_path = font_dir / 'seguisym.ttf'
if icon_font_path.exists():
    try:
        pdfmetrics.registerFont(TTFont('Icons', str(icon_font_path)))
        ICON_FONT = 'Icons'
    except Exception:
        ICON_FONT = None

# ── Colour palette ─────────────────────────────────────────────────────────
DARK_BLUE  = colors.HexColor('#1B3A5C')
ACCENT     = colors.HexColor('#2E6DA4')
GRAY       = colors.HexColor('#555555')
RULE_COLOR = colors.HexColor('#B0C4D8')
TEXT       = colors.HexColor('#1A1A1A')

# ── Paragraph styles ───────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

NAME_STYLE    = S('Name',    fontName=f'{F}-Bold',   fontSize=26, textColor=DARK_BLUE,
                  alignment=TA_CENTER, spaceAfter=1*mm,  leading=30)
SUB_STYLE     = S('Sub',     fontName=F,             fontSize=13, textColor=ACCENT,
                  alignment=TA_CENTER, spaceAfter=1.5*mm, leading=16)
CONTACT_STYLE = S('Contact', fontName=F,             fontSize=9,  textColor=GRAY,
                  alignment=TA_CENTER, spaceAfter=5*mm,  leading=12)
H2_STYLE      = S('H2',     fontName=f'{F}-Bold',   fontSize=12, textColor=DARK_BLUE,
                  spaceBefore=5*mm, spaceAfter=2*mm, leading=16)
H3_STYLE      = S('H3',     fontName=f'{F}-Bold',   fontSize=11, textColor=TEXT,
                  spaceBefore=3*mm, spaceAfter=1*mm, leading=14)
BODY_STYLE    = S('Body',   fontName=F,             fontSize=10, textColor=TEXT,
                  spaceAfter=1.5*mm, leading=14)
BULLET_STYLE  = S('Bullet', fontName=F,             fontSize=10, textColor=TEXT,
                  leftIndent=5*mm, spaceAfter=1*mm, leading=13)
STACK_STYLE   = S('Stack',  fontName=f'{F}-Italic', fontSize=9,  textColor=GRAY,
                  spaceAfter=3*mm, leading=12)

# ── Markdown helpers ───────────────────────────────────────────────────────
def escape_xml(text: str) -> str:
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def remove_emoji(text: str) -> str:
    """Remove emoji characters that Arial font doesn't support."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U00002600-\U000027BF"  # misc symbols & dingbats
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text).strip()

def convert_markdown_links(text: str) -> str:
    """Convert markdown links [text](url) to just the text."""
    return re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

def md_inline(text: str) -> str:
    """Convert **bold** and *italic* markdown to ReportLab XML tags."""
    text = escape_xml(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)
    return text

def icon(key: str) -> str:
    """Inline icon-font tag for a contact-info glyph, or '' if no icon font loaded."""
    if not ICON_FONT:
        return ''
    ch = ICONS.get(key)
    if not ch:
        return ''
    return f'<font name="{ICON_FONT}" size="9" color="#555555">{ch}</font> '

def add_contact_icon(segment: str) -> str:
    """Detect the contact-info type of a header segment and prefix it with an icon."""
    link_match = re.match(r'^\[([^\]]+)\]\(([^)]+)\)$', segment.strip())
    if link_match:
        label, url = link_match.group(1), link_match.group(2)
        url_l = url.lower()
        if 'linkedin' in url_l:
            return f'{icon("link")}<b>LinkedIn:</b> {escape_xml(label)}'
        if 'github' in url_l:
            username = label.split('/')[-1] if '/' in label else label
            return f'{icon("link")}<b>GitHub:</b> {escape_xml(username)}'
        return f'{icon("link")}{escape_xml(label)}'

    text = segment.strip()
    if re.match(r'^[\w.+-]+@[\w.-]+\.\w+$', text):
        return f'{icon("email")}{escape_xml(text)}'
    if re.match(r'^\+?[\d][\d\s().-]{5,}$', text):
        return f'{icon("phone")}{escape_xml(text)}'
    if 'linkedin.com' in text.lower():
        return f'{icon("link")}<b>LinkedIn:</b> {escape_xml(text)}'
    if 'github.com' in text.lower():
        username = text.rstrip('/').split('/')[-1]
        return f'{icon("link")}<b>GitHub:</b> {escape_xml(username)}'
    # Fallback: treat as a location / generic line
    return f'{icon("location")}{escape_xml(text)}'

def parse_markdown_table(lines: list, start_idx: int) -> tuple:
    """Parse a markdown table starting at start_idx. Returns (table_data, end_idx)."""
    table_rows = []
    i = start_idx

    # Parse header row
    if i < len(lines) and lines[i].strip().startswith('|'):
        header_cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
        table_rows.append([md_inline(c) if c else '' for c in header_cells])
        i += 1

        # Skip separator row
        if i < len(lines) and re.match(r'^\|[\s\-|]+\|$', lines[i].strip()):
            i += 1

        # Parse data rows
        while i < len(lines) and lines[i].strip().startswith('|'):
            if re.match(r'^\|[\s\-|]+\|$', lines[i].strip()):
                i += 1
                continue
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            table_rows.append([md_inline(c) if c else '' for c in cells])
            i += 1

    return table_rows, i

def create_skills_table(table_data: list) -> Table:
    """Create a styled ReportLab Table for skills matrix."""
    # Convert string content to Paragraph objects for better text wrapping
    para_rows = []
    for row_idx, row in enumerate(table_data):
        para_row = []
        for cell_idx, cell in enumerate(row):
            if row_idx == 0:  # Header row
                style = ParagraphStyle(
                    'TableHeader',
                    fontName=f'{F}-Bold',
                    fontSize=10,
                    textColor=DARK_BLUE,
                    alignment=TA_LEFT,
                )
            else:
                style = ParagraphStyle(
                    'TableBody',
                    fontName=F,
                    fontSize=9,
                    textColor=TEXT,
                    alignment=TA_LEFT,
                )
            para_row.append(Paragraph(cell, style))
        para_rows.append(para_row)

    tbl = Table(para_rows, colWidths=[40*mm, 110*mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8EEF5')),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFD')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D0D8E0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return tbl

def hr():
    return HRFlowable(width='100%', thickness=0.8, color=RULE_COLOR,
                      spaceAfter=3*mm, spaceBefore=1*mm)

# ── Parse markdown into flowables ──────────────────────────────────────────
text  = md_path.read_text(encoding='utf-8')
lines = text.splitlines()

story = []
i = 0
header_done = False   # True after the H1 + subtitle + contact block
skip_section = False  # True when we enter a section to exclude (Gap Analysis)

while i < len(lines):
    line = lines[i]

    # ── Stop / skip sections not wanted in the resume PDF ──────────────────
    if re.match(r'^##\s+Gap Analysis', line, re.IGNORECASE):
        break   # everything after this is editorial notes

    # ── H1 — candidate name ───────────────────────────────────────────────
    if line.startswith('# '):
        name = line[2:].strip()
        story.append(Paragraph(escape_xml(name), NAME_STYLE))
        # Next non-empty line is subtitle, then contact
        j = i + 1
        subtitle_added = False
        contact_lines = []
        while j < len(lines):
            nxt = lines[j].strip()
            if nxt == '' and (subtitle_added or contact_lines):
                break
            if nxt and not subtitle_added:
                nxt_clean = remove_emoji(nxt)
                nxt_clean = convert_markdown_links(nxt_clean)
                story.append(Paragraph(md_inline(nxt_clean), SUB_STYLE))
                subtitle_added = True
            elif nxt and subtitle_added:
                # Collect all contact lines (can be multiple), icon-tagging each segment
                segments = [remove_emoji(seg.strip()) for seg in nxt.split('|')]
                contact_lines.append(' · '.join(add_contact_icon(seg) for seg in segments if seg))
            j += 1

        # Add all contact lines together
        if contact_lines:
            combined_contact = ' · '.join(contact_lines)
            story.append(Paragraph(combined_contact, CONTACT_STYLE))
        i = j + 1
        header_done = True
        continue

    # ── Horizontal rule ────────────────────────────────────────────────────
    if line.strip() == '---':
        story.append(hr())
        i += 1
        continue

    # ── H2 — section header ───────────────────────────────────────────────
    if line.startswith('## '):
        title = line[3:].strip()
        story.append(Paragraph(escape_xml(title).upper(), H2_STYLE))
        i += 1
        continue

    # ── H3 — company / institution ────────────────────────────────────────
    if line.startswith('### '):
        title = line[4:].strip()
        story.append(Paragraph(escape_xml(title), H3_STYLE))
        i += 1
        continue

    # ── Bullet point ──────────────────────────────────────────────────────
    if line.startswith('- '):
        content = md_inline(line[2:].strip())
        story.append(Paragraph(f'• {content}', BULLET_STYLE))
        i += 1
        continue

    # ── Table rows (| col | col |) — render as styled table ─────────────────
    if line.strip().startswith('|'):
        # Check if this is the start of a table by looking ahead
        table_data, next_i = parse_markdown_table(lines, i)
        if table_data:
            tbl = create_skills_table(table_data)
            story.append(tbl)
            story.append(Spacer(1, 3*mm))
            i = next_i
            continue
        else:
            i += 1
            continue

    # ── Bold job-title / date line  e.g.  **Title** | date ────────────────
    if line.startswith('**') and '|' in line:
        story.append(Paragraph(md_inline(line), BODY_STYLE))
        i += 1
        continue

    # ── Primary Tech Stack line ────────────────────────────────────────────
    if line.startswith('**Primary Tech Stack'):
        story.append(Paragraph(md_inline(line), STACK_STYLE))
        i += 1
        continue

    # ── Empty line ─────────────────────────────────────────────────────────
    if line.strip() == '':
        story.append(Spacer(1, 2*mm))
        i += 1
        continue

    # ── Default — regular paragraph text ──────────────────────────────────
    story.append(Paragraph(md_inline(line), BODY_STYLE))
    i += 1

# ── Build PDF ──────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=A4,
    leftMargin=18*mm, rightMargin=18*mm,
    topMargin=16*mm,  bottomMargin=16*mm,
    title=md_path.stem,
)
doc.build(story)
print('Wrote', pdf_path)

# ── Build DOCX (basic, unchanged behaviour) ────────────────────────────────
# lines_all = md_path.read_text(encoding='utf-8').splitlines()
# doc2 = Document()
# for line in lines_all:
#     doc2.add_paragraph('' if line.strip() == '' else line)
# doc2.save(docx_path)
# print('Wrote', docx_path)
