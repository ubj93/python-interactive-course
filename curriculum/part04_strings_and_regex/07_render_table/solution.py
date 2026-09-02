"""Reference solutions for render_table."""
from typing import Any, List, Sequence


def _is_number(cell: Any) -> bool:
    # bool subclasses int, so exclude it explicitly: True is text in a report.
    return isinstance(cell, (int, float)) and not isinstance(cell, bool)


def _render(cell: Any) -> str:
    return "-" if cell is None else str(cell)


# Best practice: validate, render every cell to text once, compute widths per column,
# then format with a nested width in the spec: f"{text:{align}{width}}".
def render_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    if not headers:
        raise ValueError("headers must not be empty")
    for row in rows:
        if len(row) != len(headers):
            raise ValueError(f"row has {len(row)} cells, expected {len(headers)}: {row!r}")

    text_rows = [[_render(c) for c in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in text_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    lines: List[str] = []
    lines.append("  ".join(f"{h:<{w}}" for h, w in zip(headers, widths)))
    lines.append("  ".join("-" * w for w in widths))
    for raw, texts in zip(rows, text_rows):
        cells = []
        for value, text, w in zip(raw, texts, widths):
            align = ">" if _is_number(value) else "<"
            cells.append(f"{text:{align}{w}}")
        lines.append("  ".join(cells))
    return "\n".join(line.rstrip() for line in lines)


# Clever: transpose with zip(*...) to compute widths column-wise, and use
# str.ljust / str.rjust instead of a format spec. Same output, different tools.
def render_table_zip(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    if not headers:
        raise ValueError("headers must not be empty")
    if any(len(r) != len(headers) for r in rows):
        raise ValueError("every row needs one cell per header")
    table = [list(headers)] + [[_render(c) for c in r] for r in rows]
    widths = [max(len(c) for c in col) for col in zip(*table)]

    def line(cells: Sequence[str], raw: Sequence[Any]) -> str:
        parts = [
            c.rjust(w) if _is_number(v) else c.ljust(w)
            for c, v, w in zip(cells, raw, widths)
        ]
        return "  ".join(parts).rstrip()

    out = [line(table[0], headers), "  ".join("-" * w for w in widths)]
    out += [line(cells, raw) for cells, raw in zip(table[1:], rows)]
    return "\n".join(out)
