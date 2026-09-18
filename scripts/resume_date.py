#!/usr/bin/env python3
"""Today's date in the timezone of the resume location, not the machine's.

The cover letter carries a date, and the application folder is named
`{YYYYMMDD}`. Both should read as the candidate wrote them: the date where the
resume says the candidate lives, not wherever the machine running this pipeline
happens to sit. A run from a UTC+9 machine at 08:00 would otherwise date a Saint
Louis letter a full day ahead of the candidate's own calendar.

The zone comes from `input/profile.md` section 4, "Resume Location":

    ### Resume Location

    - **City:** Saint Louis
    - **State:** Missouri (MO)
    - **Country:** USA
    - **Timezone:** America/Chicago     <- optional, wins when present

Without an explicit `Timezone:` line the state abbreviation resolves it, which
covers every US state sitting in exactly one zone. States split across two zones
(FL, IN, KS, KY, MI, ND, NE, OR, SD, TX) have no single right answer, so they
must carry the explicit line rather than be guessed at.

Usage:
    python scripts/resume_date.py              -> September 18, 2026
    python scripts/resume_date.py --folder     -> 20260918
    python scripts/resume_date.py --json       -> both, plus the zone used
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROFILE = Path(__file__).resolve().parent.parent / 'input' / 'profile.md'

# One zone per state, for the states that have one. A split state is absent on
# purpose: guessing between Eastern and Central for Florida would silently date
# some letters wrong, so the profile has to say which.
STATE_ZONES = {
    'AL': 'America/Chicago',    'AK': 'America/Anchorage',   'AZ': 'America/Phoenix',
    'AR': 'America/Chicago',    'CA': 'America/Los_Angeles', 'CO': 'America/Denver',
    'CT': 'America/New_York',   'DC': 'America/New_York',    'DE': 'America/New_York',
    'GA': 'America/New_York',   'HI': 'Pacific/Honolulu',    'IA': 'America/Chicago',
    'ID': 'America/Denver',     'IL': 'America/Chicago',     'LA': 'America/Chicago',
    'MA': 'America/New_York',   'MD': 'America/New_York',    'ME': 'America/New_York',
    'MN': 'America/Chicago',    'MO': 'America/Chicago',     'MS': 'America/Chicago',
    'MT': 'America/Denver',     'NC': 'America/New_York',    'NH': 'America/New_York',
    'NJ': 'America/New_York',   'NM': 'America/Denver',      'NV': 'America/Los_Angeles',
    'NY': 'America/New_York',   'OH': 'America/New_York',    'OK': 'America/Chicago',
    'PA': 'America/New_York',   'RI': 'America/New_York',    'SC': 'America/New_York',
    'TN': 'America/Chicago',    'UT': 'America/Denver',      'VA': 'America/New_York',
    'VT': 'America/New_York',   'WA': 'America/Los_Angeles', 'WI': 'America/Chicago',
    'WV': 'America/New_York',   'WY': 'America/Denver',
}

SPLIT_STATES = {'FL', 'IN', 'KS', 'KY', 'MI', 'ND', 'NE', 'OR', 'SD', 'TX'}

# Fallback offsets, used only when the interpreter has no tz database. Windows
# ships none and `tzdata` is not always installed, so the US zones this project
# actually dates letters in are carried here rather than left to fail.
# Value is (standard UTC offset in hours, observes US DST).
US_FALLBACK = {
    'America/New_York': (-5, True),
    'America/Chicago': (-6, True),
    'America/Denver': (-7, True),
    'America/Phoenix': (-7, False),
    'America/Los_Angeles': (-8, True),
    'America/Anchorage': (-9, True),
    'Pacific/Honolulu': (-10, False),
}


def read_location(profile: Path = PROFILE) -> dict[str, str]:
    """The `- **Key:** value` lines under the "Resume Location" heading."""
    if not profile.is_file():
        raise SystemExit(f'{profile} not found: the resume location lives there')

    text = profile.read_text(encoding='utf-8')
    block = re.search(
        r'###\s+Resume Location\s*\n(.*?)(?=\n#{2,3}\s|\n---|\Z)', text, re.S
    )
    if not block:
        raise SystemExit(
            f'{profile} has no "### Resume Location" section, so the timezone '
            f'cannot be resolved. Add it under section 4.'
        )

    fields = {}
    for key, value in re.findall(
        r'^\s*-\s*\*\*(.+?):\*\*\s*(.+?)\s*$', block.group(1), re.M
    ):
        fields[key.strip().lower()] = value.strip()
    return fields


def resolve_zone(fields: dict[str, str]) -> str:
    """Zone name from the explicit field, else from the state abbreviation."""
    explicit = fields.get('timezone') or fields.get('time zone')
    if explicit and explicit.lower() not in {'not recorded', 'none', 'n/a'}:
        return explicit

    state = fields.get('state', '')
    abbrev = re.search(r'\(([A-Za-z]{2})\)', state)
    code = (abbrev.group(1) if abbrev else state.strip()).upper()

    if code in SPLIT_STATES:
        raise SystemExit(
            f'{code} spans more than one timezone, so it cannot be inferred. '
            f'Add `- **Timezone:** <IANA name>` under "### Resume Location" in '
            f'{PROFILE}.'
        )
    if code not in STATE_ZONES:
        raise SystemExit(
            f'no timezone known for resume location state {state!r}. Add '
            f'`- **Timezone:** <IANA name>` under "### Resume Location" in '
            f'{PROFILE}.'
        )
    return STATE_ZONES[code]


def _us_dst_bounds(year: int) -> tuple[datetime, datetime]:
    """Second Sunday in March to first Sunday in November, both at 02:00."""
    march = datetime(year, 3, 1)
    second_sunday = march + timedelta(days=(6 - march.weekday()) % 7 + 7)
    november = datetime(year, 11, 1)
    first_sunday = november + timedelta(days=(6 - november.weekday()) % 7)
    return second_sunday.replace(hour=2), first_sunday.replace(hour=2)


def now_in(zone: str) -> datetime:
    """Current wall-clock time in `zone`, tz database or not."""
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo(zone))
    except Exception:
        pass

    if zone not in US_FALLBACK:
        raise SystemExit(
            f'no tz database available and {zone} is not one of the zones this '
            f'script carries offsets for. Install one with: pip install tzdata'
        )

    std_offset, observes_dst = US_FALLBACK[zone]
    local = (datetime.now(timezone.utc) + timedelta(hours=std_offset)).replace(tzinfo=None)
    if observes_dst:
        start, end = _us_dst_bounds(local.year)
        if start <= local < end:
            local += timedelta(hours=1)
    return local


def resolve_dates() -> dict[str, str]:
    """Letter date, folder date and the zone both were taken from."""
    zone = resolve_zone(read_location())
    today = now_in(zone)
    return {
        'letter': f'{today.strftime("%B")} {today.day}, {today.year}',
        'folder': today.strftime('%Y%m%d'),
        'timezone': zone,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Today in the resume location timezone.'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--folder', action='store_true',
        help='print YYYYMMDD, the output folder name'
    )
    group.add_argument(
        '--json', action='store_true',
        help='print letter date, folder date and zone as JSON'
    )
    args = parser.parse_args(argv)

    dates = resolve_dates()
    if args.json:
        print(json.dumps(dates, indent=2))
    elif args.folder:
        print(dates['folder'])
    else:
        print(dates['letter'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
