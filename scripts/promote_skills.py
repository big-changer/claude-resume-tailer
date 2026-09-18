"""Promote newly evidenced skills out of rules.unevidenced in input/skill-map.json.

The inverse of scripts/absorb_skills.py. Absorption puts a job description's
skill into a Technical Skills row and bars it from every claim; promotion lifts
that bar once input/projects.md actually carries the skill on a `Skills used`
line, so a bullet may finally name it.

The proof comes from the file, never from an argument. This script re-reads
input/projects.md and promotes only what it can find there, which is what stops
a confident conversation from unlocking a claim the record does not support.

Run:
    python scripts/promote_skills.py
    python scripts/promote_skills.py --dry-run
    python scripts/promote_skills.py --only RabbitMQ --only MongoDB
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resume_date import resolve_dates  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SKILL_MAP = ROOT / 'input' / 'skill-map.json'
PROJECTS = ROOT / 'input' / 'projects.md'

# Below this length a value collides with ordinary prose, so a `Skills used`
# hit is not trustworthy enough to unlock a claim on.
MIN_CHARS = 3

# Product names that are also ordinary English words: matched as written, so
# "customer segment" in a project's prose cannot promote "Segment".
CASE_SENSITIVE = frozenset({
    'segment', 'temporal', 'sentry', 'poetry', 'yarn', 'backstage', 'pinecone',
})


def skills_used_lines(text: str) -> list[str]:
    """Every `Skills used` line in the project library, continuations included.

    An entry wraps its skills across several indented lines, so the list runs
    from the bullet to the next bullet or blank line.
    """
    out, collecting, buf = [], False, []
    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r'^-\s+\*\*Skills used:?\*\*', line, re.I):
            collecting, buf = True, [re.sub(r'^-\s+\*\*Skills used:?\*\*', '', line, flags=re.I)]
            continue
        if collecting:
            if not line or line.startswith('- **') or line.startswith('#'):
                out.append(' '.join(buf))
                collecting, buf = False, []
            else:
                buf.append(line)
    if buf:
        out.append(' '.join(buf))
    return out


def pattern(value: str) -> re.Pattern[str]:
    body = r'\s+'.join(re.escape(p) for p in value.split())
    lead = r'(?<![\w+#])(?<!\w\.)' if value[0].isalnum() else ''
    trail = r'(?![\w+#])(?!\.\w)' if value[-1].isalnum() else ''
    flags = 0 if value.lower() in CASE_SENSITIVE or len(value) < 4 else re.IGNORECASE
    return re.compile(lead + body + trail, flags)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--dry-run', action='store_true',
                    help='print what would be promoted and write nothing')
    ap.add_argument('--only', action='append', metavar='VALUE', default=None,
                    help='consider just this value; repeatable')
    args = ap.parse_args(argv)

    if not PROJECTS.is_file():
        raise SystemExit(f'{PROJECTS} not found: nothing can be promoted without the '
                         f'project record that would evidence it')

    evidence = '\n'.join(skills_used_lines(PROJECTS.read_text(encoding='utf-8')))
    if not evidence.strip():
        raise SystemExit('no `Skills used` lines found in input/projects.md')

    with SKILL_MAP.open(encoding='utf-8') as fh:
        data = json.load(fh)
    unevidenced = data['rules'].get('unevidenced', [])

    wanted = {v.lower() for v in (args.only or [])}
    promoted, kept = [], []
    for value in unevidenced:
        if wanted and value.lower() not in wanted:
            kept.append(value)
            continue
        if len(value) >= MIN_CHARS and pattern(value).search(evidence):
            promoted.append(value)
        else:
            kept.append(value)

    if args.only:
        for name in args.only:
            if not any(p.lower() == name.lower() for p in promoted):
                print(f'  not promoted: {name} (no `Skills used` line in '
                      f'input/projects.md carries it)')

    if not promoted:
        print('nothing to promote; no rules.unevidenced value is carried by a '
              '`Skills used` line in input/projects.md')
        return 0

    data['rules']['unevidenced'] = kept
    data['version'] = int(data.get('version', 0)) + 1
    folder = resolve_dates()['folder']
    data['updated'] = f'{folder[:4]}-{folder[4:6]}-{folder[6:]}'

    print(f'promoted {len(promoted)} value(s), map version {data["version"]}: '
          f'now claimable in a bullet')
    for value in promoted:
        print(f'  - {value}')
    print(f'{len(kept)} value(s) still listed-only')

    if args.dry_run:
        print('dry run: input/skill-map.json unchanged')
        return 0

    with SKILL_MAP.open('w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    print(f'wrote {SKILL_MAP}')
    print('Next: add each promoted skill to Section 1 of the input/master-resume-*.md '
          'tracks it belongs to, so track selection can see it.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
