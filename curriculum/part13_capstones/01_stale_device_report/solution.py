"""Reference solution for stale_device_report."""
import csv
from datetime import date
from typing import Dict, List, Optional

FIELDS = ("serial", "hostname", "user", "os", "last_checkin")


# Best practice: parse -> model -> decide -> render, each a function with one job.
# csv.DictReader handles quoting and short rows (missing columns come back as None),
# so parsing is really just normalisation and skipping.
def parse_inventory(text: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for raw in csv.DictReader(text.splitlines()):
        row = {k: (raw.get(k) or "").strip() for k in FIELDS}
        if not row["serial"]:
            continue
        row["serial"] = row["serial"].upper()
        row["hostname"] = row["hostname"].lower()
        row["user"] = row["user"].lower()
        row["os"] = row["os"] or "unknown"
        rows.append(row)
    return rows


def find_duplicates(devices: List[Dict[str, str]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for d in devices:
        counts[d["serial"]] = counts.get(d["serial"], 0) + 1
    return {s: n for s, n in counts.items() if n > 1}


def _parse_date(value: str) -> Optional[date]:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


# Collapse first, then decide. Keeping the newest check-in per serial means a
# re-enrolled machine is judged on what it did last, not on its stale old row.
def find_stale(devices: List[Dict[str, str]], today: date, max_days: int) -> List[dict]:
    best: Dict[str, dict] = {}
    for d in devices:
        current = best.get(d["serial"])
        if current is None:
            best[d["serial"]] = d
            continue
        new, old = _parse_date(d["last_checkin"]), _parse_date(current["last_checkin"])
        if new is not None and (old is None or new > old):
            best[d["serial"]] = d

    stale: List[dict] = []
    for d in best.values():
        last = _parse_date(d["last_checkin"])
        days = None if last is None else (today - last).days
        if days is None or days > max_days:
            stale.append({**d, "days": days})

    def key(row: dict):
        never = row["days"] is None
        return (row["os"].lower(), 0 if never else 1, -(row["days"] or 0), row["serial"])

    return sorted(stale, key=key)


def render_report(stale: List[dict], duplicates: Dict[str, int], today: date, max_days: int, total: int) -> str:
    never = sum(1 for r in stale if r["days"] is None)
    lines = [
        "# Stale device report",
        "",
        f"Generated: {today.isoformat()}. Cutoff: {max_days} days. Devices: {total}. "
        f"Stale: {len(stale)}. Never checked in: {never}. Duplicate serials: {len(duplicates)}.",
    ]
    if not stale:
        lines += ["", "No stale devices."]
    # Group consecutive rows by os: the input is already in report order.
    groups: List[List[dict]] = []
    for row in stale:
        if groups and groups[-1][0]["os"] == row["os"]:
            groups[-1].append(row)
        else:
            groups.append([row])
    for group in groups:
        lines += ["", f"## {group[0]['os']} ({len(group)})", "",
                  "| serial | hostname | user | last check-in | days |", "|---|---|---|---|---|"]
        for r in group:
            last = "never" if r["days"] is None else r["last_checkin"]
            days = "-" if r["days"] is None else str(r["days"])
            cells = [r["serial"], r["hostname"] or "-", r["user"] or "-", last, days]
            lines.append("| " + " | ".join(cells) + " |")
    if duplicates:
        lines += ["", "## Duplicate serials", ""]
        lines += [f"- {s} ({n} rows)" for s, n in sorted(duplicates.items())]
    return "\n".join(lines)


def stale_device_report(text: str, today: date, max_days: int) -> str:
    devices = parse_inventory(text)
    duplicates = find_duplicates(devices)
    stale = find_stale(devices, today, max_days)
    total = len({d["serial"] for d in devices})
    return render_report(stale, duplicates, today, max_days, total)
