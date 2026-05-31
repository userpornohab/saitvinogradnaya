from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable, List, Optional

MAX_BLOCKING_EVENT_DAYS = 60


@dataclass
class ICalEvent:
    uid: str
    start_date: date
    end_date: date
    summary: str = ""


def _unfold_lines(text: str) -> List[str]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    unfolded: List[str] = []
    for line in lines:
        if not line:
            continue
        if line[:1] in {" ", "\t"} and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)
    return unfolded


def _property_name(line: str) -> str:
    left = line.split(":", 1)[0]
    return left.split(";", 1)[0].upper()


def _property_value(line: str) -> str:
    return line.split(":", 1)[1] if ":" in line else ""


def _parse_ical_date(value: str) -> Optional[date]:
    value = value.strip()
    if not value:
        return None

    candidates = [
        ("%Y%m%d", value[:8]),
        ("%Y%m%dT%H%M%S", value.rstrip("Z")),
        ("%Y-%m-%d", value[:10]),
    ]
    for fmt, candidate in candidates:
        try:
            return datetime.strptime(candidate, fmt).date()
        except ValueError:
            continue
    return None


def parse_ical_events(text: str) -> List[ICalEvent]:
    events: List[ICalEvent] = []
    current = None

    for line in _unfold_lines(text):
        marker = line.upper()
        if marker == "BEGIN:VEVENT":
            current = {}
            continue
        if marker == "END:VEVENT":
            if current:
                start_date = _parse_ical_date(current.get("DTSTART", ""))
                end_date = _parse_ical_date(current.get("DTEND", ""))
                uid = current.get("UID") or f"event-{len(events) + 1}"
                summary = current.get("SUMMARY", "")

                if start_date and end_date and end_date > start_date:
                    events.append(ICalEvent(
                        uid=uid[:300],
                        start_date=start_date,
                        end_date=end_date,
                        summary=summary[:300],
                    ))
            current = None
            continue
        if current is None or ":" not in line:
            continue

        name = _property_name(line)
        if name in {"UID", "DTSTART", "DTEND", "SUMMARY"}:
            current[name] = _property_value(line)

    return events


def is_blocking_calendar_period(summary: str, start_date: date, end_date: date) -> bool:
    duration_days = (end_date - start_date).days
    normalized_summary = (summary or "").strip().lower()
    if normalized_summary == "недоступно":
        return False
    if duration_days > MAX_BLOCKING_EVENT_DAYS:
        return False
    return duration_days > 0


def _escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def collapse_busy_days(events: Iterable[ICalEvent], units_count: int) -> List[ICalEvent]:
    day_counts = {}
    units_count = max(units_count or 1, 1)

    for event in events:
        current = event.start_date
        while current < event.end_date:
            day_counts[current] = day_counts.get(current, 0) + 1
            current += timedelta(days=1)

    busy_days = sorted(day for day, count in day_counts.items() if count >= units_count)
    if not busy_days:
        return []

    ranges: List[ICalEvent] = []
    start = busy_days[0]
    previous = busy_days[0]
    for day in busy_days[1:]:
        if day == previous + timedelta(days=1):
            previous = day
            continue
        ranges.append(ICalEvent(
            uid=f"busy-{start.strftime('%Y%m%d')}-{(previous + timedelta(days=1)).strftime('%Y%m%d')}",
            start_date=start,
            end_date=previous + timedelta(days=1),
            summary="Забронировано",
        ))
        start = day
        previous = day

    ranges.append(ICalEvent(
        uid=f"busy-{start.strftime('%Y%m%d')}-{(previous + timedelta(days=1)).strftime('%Y%m%d')}",
        start_date=start,
        end_date=previous + timedelta(days=1),
        summary="Забронировано",
    ))
    return ranges


def build_ical(events: Iterable[ICalEvent], calendar_name: str = "Vinegrape availability") -> str:
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "PRODID:-//Vinegrape//Room Calendar 1.0//RU",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-TIMEZONE:Europe/Moscow",
        f"X-WR-CALNAME:{_escape_text(calendar_name)}",
    ]

    for event in events:
        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTAMP:{now}",
            f"UID:{_escape_text(event.uid)}@vinegrape.ru",
            f"DTSTART;VALUE=DATE:{event.start_date.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{event.end_date.strftime('%Y%m%d')}",
            f"SUMMARY:{_escape_text(event.summary or 'Забронировано')}",
            "TRANSP:OPAQUE",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
