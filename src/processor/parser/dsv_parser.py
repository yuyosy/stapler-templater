from typing import Any

from config import DsvOption


def parse_dsv(content: str, options: DsvOption | None) -> Any:
    if options is None:
        options = DsvOption()
    delimiter = options.delimiter
    enable_header = options.enable_header
    skip_empty_lines = options.skip_empty_lines
    comment_line = options.comment_line
    parse_type = options.parse_type

    lines = content.splitlines()
    rows = []
    for line in lines:
        if skip_empty_lines and not line.strip():
            continue
        if comment_line and line.strip().startswith(comment_line):
            continue
        rows.append(line.split(delimiter))

    if not rows:
        return [] if parse_type == "list" else []

    if parse_type == "dict":
        header = rows[0]
        data_rows = rows[1:]
        return [dict(zip(header, row)) for row in data_rows]
    else:
        if enable_header:
            return rows[1:]
        else:
            return rows
