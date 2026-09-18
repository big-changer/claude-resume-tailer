"""Merge a run's absorbed skills into input/skill-map.json.

An absorbed skill is one a job description named that the map did not carry, so
resume-jd-optimizer rendered it in a Technical Skills row this run (listed, never
claimed) and Step 8 records it here. The next posting that names it then finds it
in the map as an ordinary inventory value instead of absorbing it again.

Every value added lands in two places: the named category, and rules.unevidenced.
The second is what keeps it out of bullets, Tech Stacks lines, the summary and the
cover letter until a real project carries it on a `Skills used` line. Nothing here
grants evidence; `evidence_still_applies` still governs every claim.

Values already present under ANY label are skipped, so the no_duplicate_values rule
survives a run that guessed a different category than the map already chose. Labels
are closed: an unknown label is an error, never a tenth category.

Run:
    python scripts/absorb_skills.py --slug accuris \
        "Programming Languages=Java,Kotlin" "Frameworks & Libraries=Spring Boot"
    python scripts/absorb_skills.py --dry-run "Databases=Oracle"

Separate values with commas. A value containing a comma of its own, like
"AWS (EC2, S3)", is passed as its own argument instead.

There is a second, opposite case. A skill the candidate confirmed into
input/projects.md may be missing from this file altogether, so no resume can
render it even though a bullet could now claim it. `--evidenced` adds such a
value as an ordinary one and deliberately does NOT list it in
rules.unevidenced. It refuses anything it cannot find on a `Skills used` line
in input/projects.md, so the proof comes from the record and not from the
command line:

    python scripts/absorb_skills.py --evidenced "Architecture & Design=SFTP"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resume_date import resolve_dates  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SKILL_MAP = ROOT / 'input' / 'skill-map.json'

# Kept as a name so the module source carries no escape sequences that a
# patching heredoc can mangle.
NEWLINE = chr(10)


def load() -> dict:
    with SKILL_MAP.open(encoding='utf-8') as fh:
        return json.load(fh)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        'placements', nargs='+', metavar='LABEL=value,value',
        help='one argument per category label, using the map\'s own spelling'
    )
    ap.add_argument('--slug', default=None, help='run slug, for the summary line only')
    ap.add_argument(
        '--dry-run', action='store_true',
        help='print what would change and write nothing'
    )
    ap.add_argument(
        '--evidenced', action='store_true',
        help=('the values are already carried by a `Skills used` line in '
              'input/projects.md: add them as ordinary values, keep them out '
              'of rules.unevidenced, and refuse any the record does not carry')
    )
    return ap.parse_args(argv)


def split_placements(raw: list[str]) -> list[tuple[str, list[str]]]:
    out: list[tuple[str, list[str]]] = []
    for item in raw:
        if '=' not in item:
            raise SystemExit(
                f'not a placement: {item!r}. Expected "Label=value,value".'
            )
        label, _, values = item.partition('=')
        vals = [v.strip() for v in values.split(',') if v.strip()]
        if not vals:
            raise SystemExit(f'no values given for label {label.strip()!r}')
        out.append((label.strip(), vals))
    return out


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    placements = split_placements(args.placements)
    data = load()
    categories = data['categories']

    # --evidenced promises the record already carries these, so check the
    # record rather than taking the caller's word for it. Same parser the
    # promotion script uses, so both directions of the loop read evidence the
    # same way.
    if args.evidenced:
        from promote_skills import PROJECTS, pattern, skills_used_lines
        if not PROJECTS.is_file():
            raise SystemExit(
                f'{PROJECTS} not found: --evidenced has nothing to check against')
        evidence = NEWLINE.join(
            skills_used_lines(PROJECTS.read_text(encoding='utf-8')))
        unproven = [v for _, vals in placements for v in vals
                    if not pattern(v).search(evidence)]
        if unproven:
            raise SystemExit(
                '--evidenced refused: no `Skills used` line in '
                'input/projects.md carries '
                + ', '.join(repr(v) for v in unproven)
                + '. Confirm it into the project record first, or drop '
                  '--evidenced to add it as a listed-only value.')

    by_label = {c['label']: c for c in categories}
    by_lower = {c['label'].lower(): c for c in categories}

    # Every value the map already holds, and the label holding it.
    held: dict[str, str] = {}
    for cat in categories:
        for value in cat['values']:
            held[value.lower()] = cat['label']

    unevidenced = data['rules'].setdefault('unevidenced', [])
    unev_lower = {v.lower() for v in unevidenced}

    added: list[tuple[str, str]] = []
    skipped: list[str] = []
    promoted: list[str] = []

    for label, values in placements:
        cat = by_label.get(label) or by_lower.get(label.lower())
        if cat is None:
            raise SystemExit(
                f'unknown label {label!r}. The nine labels are closed:\n  '
                + '\n  '.join(by_label)
            )
        for value in values:
            key = value.lower()
            if key in held:
                # Already in the map, under this label or another one. Leave it
                # where it is: no_duplicate_values, and an evidenced value must
                # never be demoted into rules.unevidenced by a later run.
                skipped.append(f'{value} (already under {held[key]})')
                continue
            cat['values'].append(value)
            held[key] = cat['label']
            added.append((cat['label'], value))
            if args.evidenced:
                # Evidenced by input/projects.md, so the claim bar does not
                # apply: a bullet may name it. Never listed as unevidenced.
                continue
            if key not in unev_lower:
                unevidenced.append(value)
                unev_lower.add(key)
                promoted.append(value)

    if not added:
        print('nothing to add; every value is already in the map')
        for line in skipped:
            print(f'  skipped: {line}')
        return 0

    data['rules']['unevidenced'] = sorted(set(unevidenced), key=str.lower)
    data['version'] = int(data.get('version', 0)) + 1
    data['updated'] = resolve_dates()['folder']
    data['updated'] = f'{data["updated"][:4]}-{data["updated"][4:6]}-{data["updated"][6:]}'

    where = f' for {args.slug}' if args.slug else ''
    kind = 'added as evidenced' if args.evidenced else 'absorbed'
    print(f'{kind}{where}: {len(added)} value(s), map version {data["version"]}')
    for label, value in added:
        print(f'  + {label}: {value}')
    for line in skipped:
        print(f'  skipped: {line}')
    if not args.evidenced and len(promoted) != len(added):
        print(f'  note: {len(added) - len(promoted)} already listed as unevidenced')
    if args.evidenced:
        print('  claim bar not applied: input/projects.md carries each of these, '
              'so a bullet may name them')

    if args.dry_run:
        print('dry run: input/skill-map.json unchanged')
        return 0

    with SKILL_MAP.open('w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    print(f'wrote {SKILL_MAP}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
