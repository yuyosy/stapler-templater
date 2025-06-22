import tempfile
from pathlib import Path

import pytest

from src.config import DsvOption, TextFSMOption
from src.processor.parser.dsv_parser import parse_dsv
from src.processor.parser.json_parser import parse_json
from src.processor.parser.textfsm_parser import parse_textfsm
from src.processor.parser.xml_parser import parse_xml
from src.processor.parser.yaml_parser import parse_yaml


# JSON
@pytest.mark.parametrize(
    "content,expected",
    [
        ('{"a": 1, "b": 2}', {"a": 1, "b": 2}),
        ("[1,2,3]", [1, 2, 3]),
        ("{a: 1, b: 2}", None),
        ("[1,2,3", None),
        ("notjson", None),
    ],
)
def test_parse_json_all(content, expected):
    assert parse_json(content, None) == expected


# YAML
@pytest.mark.parametrize(
    "content,expected",
    [
        ("a: 1\nb: 2", {"a": 1, "b": 2}),
        ("- 1\n- 2\n- 3", [1, 2, 3]),
        ("a: 1\nb: [", None),
        ("- 1\n- 2\n- [", None),
        ("not: yaml: -", None),
    ],
)
def test_parse_yaml_all(content, expected):
    assert parse_yaml(content, None) == expected


# XML
@pytest.mark.parametrize(
    "content,expected_dict",
    [
        ("<root><a>1</a></root>", {"root": {"a": {"#text": "1"}}}),
        ("<data></data>", {"data": None}),
        (
            "<root attr='val'><a>1</a></root>",
            {"root": {"@attr": "val", "a": {"#text": "1"}}},
        ),
        (
            "<root><a attr='x'>1</a></root>",
            {"root": {"a": {"@attr": "x", "#text": "1"}}},
        ),
        ("<root><a>1</a>", None),  # Invalid XML (unclosed tag)
        ("<root><a>1</a></b></root>", None),  # Invalid XML (mismatched tags)
        ("plain text", None),  # Invalid XML (not well-formed)
    ],
)
def test_parse_xml_all(content, expected_dict):
    elem = parse_xml(content, None)
    assert elem == expected_dict


# DSV
@pytest.mark.parametrize(
    "content,options,expected",
    [
        (
            "a\tb\nc\td",
            DsvOption(parse_type="dict", enable_header=True),
            [{"a": "c", "b": "d"}],
        ),
        (
            "a,b\nc,d",
            DsvOption(parse_type="list", delimiter=",", enable_header=True),
            [["c", "d"]],
        ),
        (
            "a,b\nc,d",
            DsvOption(parse_type="list", delimiter=",", enable_header=False),
            [["a", "b"], ["c", "d"]],
        ),
        (
            "a\tb\n# comment\nc\td\n\n",
            DsvOption(parse_type="dict", enable_header=True, comment_line="#"),
            [{"a": "c", "b": "d"}],
        ),
        (
            "a|b\nc|d",
            DsvOption(parse_type="list", delimiter="|", enable_header=True),
            [["c", "d"]],
        ),
        (
            "a,b\nc",
            DsvOption(parse_type="list", delimiter=",", enable_header=True),
            [["c"]],
        ),
        ("", DsvOption(parse_type="dict", enable_header=True), []),
    ],
)
def test_parse_dsv_all(content, options, expected):
    assert parse_dsv(content, options) == expected


# TextFSMテンプレート内容
TESTFSM_TEMPLATE = """# TextFSM Template
Value Required Test1 (\\S+)

Start
  ^${Test1}

"""


# TextFSM
@pytest.mark.parametrize(
    "content, tpl_content, parse_type, enable_header, expected",
    [
        ("abc 123", TESTFSM_TEMPLATE, "dict", True, [{"Test1": "abc"}]),
        ("abc 123", TESTFSM_TEMPLATE, "list", False, [["abc"]]),
        ("abc 123", TESTFSM_TEMPLATE, "dict", True, [{"Test1": "abc"}]),
        ("abc 123", TESTFSM_TEMPLATE, "list", True, [["Test1"], ["abc"]]),
        ("abc 123", TESTFSM_TEMPLATE, "list", False, [["abc"]]),
        ("abc 123", None, "dict", True, None),  # テンプレートなし
        ("", TESTFSM_TEMPLATE, "dict", True, []),
    ],
)
def test_parse_textfsm_all(content, tpl_content, parse_type, enable_header, expected):
    if tpl_content is not None:
        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, encoding="utf-8", suffix=".textfsm"
        ) as tf:
            tf.write(tpl_content)
            tf.flush()
            tpl_path = tf.name
    else:
        tpl_path = "notfound.textfsm"
    options = TextFSMOption(
        template=tpl_path,
        parse_type=parse_type,
        enable_header=enable_header,
    )
    try:
        assert parse_textfsm(content, options) == expected
    finally:
        if tpl_content is not None:
            Path(tpl_path).unlink(missing_ok=True)
