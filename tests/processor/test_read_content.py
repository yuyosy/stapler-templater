import tempfile
from pathlib import Path

import pytest

from src.config import ReadContentExtractOption, ReadContentOption
from src.processor.read_content import read_content

# テストデータ
TEST_CONTENT = (
    "line1: foo\nline2: bar\nline3: baz\nline4: 123\nline5: barfoo\nline6: end\n"
)


@pytest.mark.parametrize(
    "option,expected",
    [
        # --- 全体 ---
        (
            None,
            "line1: foo\nline2: bar\nline3: baz\nline4: 123\nline5: barfoo\nline6: end\n",
        ),
        # --- index ---
        (
            ReadContentOption(
                start=ReadContentExtractOption(extract_type="index", target=7)
            ),
            "foo\nline2: bar\nline3: baz\nline4: 123\nline5: barfoo\nline6: end\n",
        ),
        (
            ReadContentOption(
                end=ReadContentExtractOption(extract_type="index", target=10)
            ),
            "line1: foo",
        ),
        (
            ReadContentOption(
                start=ReadContentExtractOption(
                    extract_type="index", target=7, include_match=False
                )
            ),
            "foo\nline2: bar\nline3: baz\nline4: 123\nline5: barfoo\nline6: end\n",
        ),
        # --- line ---
        (
            ReadContentOption(
                start=ReadContentExtractOption(extract_type="line", target=3),
                end=ReadContentExtractOption(extract_type="line", target=4),
            ),
            "line3: baz\nline4: 123\nline5: barfoo\n",
        ),
        (
            ReadContentOption(
                start=ReadContentExtractOption(
                    extract_type="line", target=3, include_match=False
                )
            ),
            "line3: baz\nline4: 123\nline5: barfoo\nline6: end\n",
        ),
        # --- exact ---
        (
            ReadContentOption(
                start=ReadContentExtractOption(extract_type="exact", target="bar"),
                end=ReadContentExtractOption(extract_type="exact", target="line5"),
            ),
            "bar\nline3: baz\nline4: 123\nline5",
        ),
        (
            ReadContentOption(
                start=ReadContentExtractOption(
                    extract_type="exact", target="bar", include_match=False
                ),
                end=ReadContentExtractOption(
                    extract_type="exact", target="line5", include_match=False
                ),
            ),
            "\nline3: baz\nline4: 123\n",
        ),
        # --- regex ---
        (
            ReadContentOption(
                start=ReadContentExtractOption(
                    extract_type="regex", target="line[2-4]"
                ),
                end=ReadContentExtractOption(extract_type="regex", target="foo|end"),
            ),
            "line2: bar\nline3: baz\nline4: 123\nline5: barfoo",
        ),
        (
            ReadContentOption(
                start=ReadContentExtractOption(extract_type="regex", target="line2"),
                end=ReadContentExtractOption(extract_type="regex", target="barfoo"),
            ),
            "line2: bar\nline3: baz\nline4: 123\nline5: barfoo",
        ),
        (
            ReadContentOption(
                start=ReadContentExtractOption(
                    extract_type="regex", target="line2", include_match=False
                ),
                end=ReadContentExtractOption(
                    extract_type="regex", target="barfoo", include_match=False
                ),
            ),
            ": bar\nline3: baz\nline4: 123\nline5: ",
        ),
        # --- auto ---
        (
            ReadContentOption(
                start=ReadContentExtractOption(extract_type="auto", target="")
            ),
            "line1: foo\nline2: bar\nline3: baz\nline4: 123\nline5: barfoo\nline6: end\n",
        ),
    ],
)
def test_read_content(option, expected):
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8") as tf:
        tf.write(TEST_CONTENT)
        tf.flush()
        tf_path = Path(tf.name)
    try:
        result = read_content(tf_path, option)
        assert result == expected
    finally:
        tf_path.unlink(missing_ok=True)
