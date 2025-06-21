import os

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
    ],
)
def test_parse_json(content, expected):
    assert parse_json(content, None) == expected


# YAML
@pytest.mark.parametrize(
    "content,expected",
    [
        ("a: 1\nb: 2", {"a": 1, "b": 2}),
        ("- 1\n- 2\n- 3", [1, 2, 3]),
    ],
)
def test_parse_yaml(content, expected):
    assert parse_yaml(content, None) == expected


# XML
@pytest.mark.parametrize(
    "content,expected_tag",
    [
        ("<root><a>1</a></root>", "root"),
        ("<data></data>", "data"),
    ],
)
def test_parse_xml(content, expected_tag):
    elem = parse_xml(content, None)
    assert elem.tag == expected_tag  # type: ignore


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
    ],
)
def test_parse_dsv(content, options, expected):
    assert parse_dsv(content, options) == expected


@pytest.mark.parametrize(
    "content, tpl, parse_type, enable_header, expected",
    [
        ("abc 123", "test.textfsm", "dict", True, [{"Test1": "abc"}]),
        ("abc 123", "test.textfsm", "list", False, [["abc"]]),
        ("abc 123", "test.textfsm", "dict", True, [{"Test1": "abc"}]),
        ("abc 123", "test.textfsm", "list", True, [["Test1"], ["abc"]]),
        ("abc 123", "test.textfsm", "list", False, [["abc"]]),
    ],
)
def test_parse_textfsm(content, tpl, parse_type, enable_header, expected):
    tpl_path = os.path.join("tests", "data", tpl)
    options = TextFSMOption(
        template=tpl_path,
        parse_type=parse_type,
        enable_header=enable_header,
    )
    result = parse_textfsm(content, options)
    assert result == expected
