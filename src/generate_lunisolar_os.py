#!/usr/bin/env python3
"""
Lunisolar OS calendar generator (astronomy-accurate moon phases via Skyfield).

Generates:
- calendar/lunisolar_os_<YEAR>.ics
- calendar/lunisolar_os_latest.ics (optional copy step in workflow)

Windows:
New→First (Build), First→Full (Execute), Full→Third (Review), Third→New (Refine)

All-day events are created using Europe/London local dates.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone, date
from zoneinfo import ZoneInfo

from skyfield import almanac
from skyfield.api import load


LONDON = ZoneInfo("Europe/London")

WINDOW_GUIDANCE = {
    ("New Moon", "First Quarter"): ("🌑→🌓 Build", "Waxing Crescent",
        "Set intentions, plan your week, and define 1–3 process goals.\n"
        "Trading: finalize rules, mark levels, pre-commit risk limits.\n"
        "Keep it clean: simple actions that compound."),
    ("First Quarter", "Full Moon"): ("🌓→🌕 Execute", "Waxing Gibbous",
        "Execution + discipline.\n"
        "Trading: A+ setups only, strict risk, no revenge trades.\n"
        "Build reps, not excitement. Track mistakes like a scientist."),
    ("Full Moon", "Third Quarter"): ("🌕→🌗 Review", "Waning Gibbous",
        "Reflection and truth.\n"
        "Trading: review winners/losers, extract 1 lesson, reduce noise.\n"
        "Journal insights. Release emotional residue."),
    ("Third Quarter", "New Moon"): ("🌗→🌑 Refine", "Waning Crescent",
        "Prune and reset.\n"
        "Trading: simplify watchlist, cut weak habits, lower size if needed.\n"
        "Protect sleep/energy. Prepare the next cycle."),
}

PHASE_DAY_GUIDANCE = {
    "New Moon": ("🌑 New Moon — Plan",
        "Planning + intentions.\n"
        "Write 3 priorities, define risk rules, and choose the smallest daily actions that compound."),
    "First Quarter": ("🌓 First Quarter — Commit",
        "Commit to action.\n"
        "Execute your process. One day at a time. No perfectionism."),
    "Full Moon": ("🌕 Full Moon — Reveal",
        "Clarity + truth.\n"
        "Review the cycle, journal insights, and release what’s weighing you down."),
    "Third Quarter": ("🌗 Third Quarter — Edit",
        "Course-correct.\n"
        "Reduce noise, refine rules, and protect sleep/energy."),
}

SEASONS = [
    # Day-level anchors (good enough for the OS layer)
    ((3, 20), "☀️ March Equinox", "Balance point. Clean reset: choose what you’re becoming; build routines that make it inevitable."),
    ((6, 21), "☀️ June Solstice", "Peak light. Max output. Guard against overtrading—channel power into process."),
    ((9, 23), "☀️ September Equinox", "Second balance. Audit systems: what’s working? Re-align goals for the rest of the year."),
    ((12, 21), "☀️ December Solstice", "Deep reset. Review the year; design the next. Rest is strategy."),
]

WHEEL = [
    ((2, 1),  "🔥 Imbolc (cross-quarter)",      "First stirrings of spring. Commit to small daily practice; momentum builds quietly."),
    ((5, 1),  "🌼 Beltane (cross-quarter)",     "Growth + vitality. Expand what works; celebrate progress; keep boundaries."),
    ((8, 1),  "🌾 Lughnasadh (cross-quarter)",  "First harvest. Measure results, harvest lessons, refine strategy."),
    ((11, 1), "🕯 Samhain (cross-quarter)",     "Threshold season. Close loops, let go of dead weight, simplify."),
]


def ics_escape(s: str) -> str:
    return (
        s.replace("\\", "\\\\")
         .replace("\n", "\\n")
         .replace(",", "\\,")
         .replace(";", "\\;")
    )


def ymd(d: date) -> str:
    return d.strftime("%Y%m%d")


def uid(tag: str) -> str:
    # Stable-ish UID tag; good enough for subscribed calendars
    return f"{tag}@lunisolar-os"


def moon_phase_events(year: int):
    """
    Returns a list of (utc_dt, phase_name) covering [Jan 1, Jan 1 next year).
    Phases use almanac.moon_phases: 0 New, 1 First, 2 Full, 3 Last.
    """
    ts = load.timescale()
    eph = load("de421.bsp")  # auto-downloads on first run in GitHub Actions
    t0 = ts.utc(year, 1, 1, 0, 0, 0)
    t1 = ts.utc(year + 1, 1, 1, 0, 0, 0)

    f = almanac.moon_phases(eph)
    t, y = almanac.find_discrete(t0, t1, f)

    name = {0: "New Moon", 1: "First Quarter", 2: "Full Moon", 3: "Third Quarter"}
    out = []
    for ti, yi in zip(t, y):
        utc_dt = ti.utc_datetime().replace(tzinfo=timezone.utc)
        out.append((utc_dt, name[int(yi)]))
    return out


def generate_ics(year: int, include_wheel: bool = True) -> str:
    events = moon_phase_events(year)

    # Convert to London local dates for all-day bars
    points = [(dt.astimezone(LONDON).date(), phase) for dt, phase in events]
    points.sort()

    nowstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Lunisolar OS//Accurate Moon Phases//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    def add_all_day(summary: str, desc: str, start_d: date, end_excl: date, uid_tag: str):
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid(uid_tag)}",
            f"DTSTAMP:{nowstamp}",
            f"DTSTART;VALUE=DATE:{ymd(start_d)}",
            f"DTEND;VALUE=DATE:{ymd(end_excl)}",
            f"SUMMARY:{ics_escape(summary)}",
            f"DESCRIPTION:{ics_escape(desc)}",
            "END:VEVENT",
        ])

    # Phase windows (bars)
    for i in range(len(points) - 1):
        s_date, s_phase = points[i]
        e_date, e_phase = points[i + 1]

        key = (s_phase, e_phase)
        if key not in WINDOW_GUIDANCE:
            continue

        title, name, desc = WINDOW_GUIDANCE[key]

        # If two phase events land on same local date, skip the bar (it would be 0-length).
        if s_date >= e_date:
            continue

        add_all_day(
            f"{title} — {name}",
            desc + "\n\nPersonal anchor:\n- Protect clarity with sleep, food, movement.\n- Trading: process > outcome.\n- Journal nightly: win, lesson, next step.",
            s_date,
            e_date,
            uid_tag=f"win-{year}-{s_phase.replace(' ','_')}-{s_date}"
        )

    # Single-day phase markers
    seen = set()
    for dt, phase in events:
        d0 = dt.astimezone(LONDON).date()
        k = (d0, phase)
        if k in seen:
            continue
        seen.add(k)

        title, desc = PHASE_DAY_GUIDANCE[phase]
        add_all_day(
            title,
            desc,
            d0,
            d0 + timedelta(days=1),
            uid_tag=f"phase-{year}-{phase.replace(' ','_')}-{d0}"
        )

    # Seasonal markers (day anchors)
    for (m, d), title, desc in SEASONS:
        d0 = date(year, m, d)
        add_all_day(title, desc, d0, d0 + timedelta(days=1), uid_tag=f"season-{year}-{m:02d}{d:02d}")

    # Wheel (optional)
    if include_wheel:
        for (m, d), title, desc in WHEEL:
            d0 = date(year, m, d)
            add_all_day(title, desc, d0, d0 + timedelta(days=1), uid_tag=f"wheel-{year}-{m:02d}{d:02d}")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--out", type=str, required=True)
    p.add_argument("--no-wheel", action="store_true")
    args = p.parse_args()

    content = generate_ics(args.year, include_wheel=not args.no_wheel)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
