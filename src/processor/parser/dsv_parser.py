from typing import Any

from config import DsvOption


def parse_dsv(content: str, options: DsvOption | None) -> Any:
    if options is None:
        options = DsvOption()

    lines = content.splitlines()
    rows = []
    for line in lines:
        if options.skip_empty_lines and not line.strip():
            continue
        if options.comment_line and line.strip().startswith(options.comment_line):
            continue
        rows.append(line.split(options.delimiter))

    if not rows:
        return [] if options.parse_type == "list" else []

    if options.parse_type == "dict":
        if options.enable_header:
            header = rows[0]
            data_rows = rows[1:]
            return [dict(zip(header, row)) for row in data_rows]
        else:
            return [{i: v for i, v in enumerate(row)} for row in rows]
    else:
        if options.enable_header:
            return rows[1:]
        else:
            return rows
