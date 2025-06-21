import re
from pathlib import Path

from loguru import logger

from config import ReadContentExtractOption, ReadContentOption


def _extract_position(
    content: str, extract_option: ReadContentExtractOption, is_start: bool
) -> int:
    if extract_option.extract_type == "auto":
        return 0 if is_start else len(content)
    elif extract_option.extract_type == "index":
        if isinstance(extract_option.extract, int):
            idx = extract_option.extract
            if idx < 0:
                return 0 if is_start else len(content)
            if idx > len(content):
                return len(content)
            return idx
        else:
            return 0 if is_start else len(content)
    elif extract_option.extract_type == "line":
        if isinstance(extract_option.extract, int):
            lines = content.splitlines(keepends=True)
            if extract_option.extract <= 0:
                return 0 if is_start else len(content)
            if extract_option.extract > len(lines):
                return len(content)
            pos = sum(len(line) for line in lines[: extract_option.extract - 1])
            return pos
        else:
            return 0 if is_start else len(content)
    elif extract_option.extract_type == "exact":
        idx = content.find(str(extract_option.extract))
        if idx == -1:
            return 0 if is_start else len(content)
        return idx if is_start else idx + len(str(extract_option.extract))
    elif extract_option.extract_type == "regex":
        m = re.search(str(extract_option.extract), content)
        if not m:
            return 0 if is_start else len(content)
        return m.start() if is_start else m.end()
    return 0 if is_start else len(content)


def read_content(file_path: Path, option: ReadContentOption | None) -> str:
    try:
        with file_path.open("r", encoding=option.encoding if option else "utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        return ""

    if option is None or (option.start is None and option.end is None):
        return content

    start_pos = 0
    end_pos = len(content)
    if option.start is not None:
        start_pos = _extract_position(content, option.start, is_start=True)
    if option.end is not None:
        end_pos = _extract_position(content, option.end, is_start=False)
    if start_pos > end_pos:
        logger.warning(
            f"start_pos({start_pos}) > end_pos({end_pos}), returning empty string."
        )
        return ""
    return content[start_pos:end_pos]
