import re
from pathlib import Path

from loguru import logger

from config import ReadContentExtractOption, ReadContentOption


def _extract_position(
    content: str, extract_option: ReadContentExtractOption, is_start: bool
) -> tuple[int, int]:
    # 返り値: (位置, マッチ長)
    if extract_option.extract_type == "auto":
        return (0 if is_start else len(content), 0)
    elif extract_option.extract_type == "index":
        if isinstance(extract_option.target, int):
            idx = extract_option.target
            if idx < 0:
                return (0 if is_start else len(content), 0)
            if idx > len(content):
                return (len(content), 0)
            return (idx, 0)
        else:
            return (0 if is_start else len(content), 0)
    elif extract_option.extract_type == "line":
        if isinstance(extract_option.target, int):
            lines = content.splitlines(keepends=True)
            if extract_option.target <= 0:
                return (0 if is_start else len(content), 0)
            if extract_option.target > len(lines):
                return (len(content), 0)
            pos = sum(len(line) for line in lines[: extract_option.target - 1])
            return (pos, 0)
        else:
            return (0 if is_start else len(content), 0)
    elif extract_option.extract_type == "exact":
        idx = content.find(str(extract_option.target))
        if idx == -1:
            return (0 if is_start else len(content), 0)
        match_len = len(str(extract_option.target))
        if is_start:
            return (idx, match_len)
        else:
            return (idx + match_len, match_len)
    elif extract_option.extract_type == "regex":
        m = re.search(str(extract_option.target), content)
        if not m:
            return (0 if is_start else len(content), 0)
        if is_start:
            return (m.start(), m.end() - m.start())
        else:
            return (m.end(), m.end() - m.start())
    return (0 if is_start else len(content), 0)


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
    start_match_len = 0
    end_match_len = 0

    if option.start is not None:
        start_pos, start_match_len = _extract_position(
            content, option.start, is_start=True
        )
    if option.end is not None:
        end_pos_rel, end_match_len = _extract_position(
            content[start_pos:], option.end, is_start=False
        )
        end_pos = start_pos + end_pos_rel

    if option.start is not None and option.start.include_match:
        pass
    elif option.start is not None and not option.start.include_match:
        start_pos += start_match_len

    if option.end is not None and option.end.include_match:
        end_pos += 0
    elif option.end is not None and not option.end.include_match:
        end_pos -= end_match_len

    if start_pos > end_pos:
        logger.warning(
            f"start_pos({start_pos}) > end_pos({end_pos}), returning empty string."
        )
        return ""
    return content[start_pos:end_pos]
