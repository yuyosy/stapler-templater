import json
import shutil
import tempfile
from pathlib import Path

import pytest

from src.config import (
    Config,
    DsvOption,
    InputOption,
    OutputOption,
    ParseOption,
    RecipeOption,
    TemplateOption,
)
from src.processor.run_recipe import run_recipe


def make_config_and_recipe(
    tmpdir, template_content="Hello {{ name }}", parse=None, output_path=None
):
    template_dir = tmpdir / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    template_file = template_dir / "test.tpl"
    template_file.write_text(template_content, encoding="utf-8")
    recipe = RecipeOption(
        enabled=True,
        id="r1",
        name="TestRecipe",
        input=InputOption(file_pattern="*.txt"),
        output=OutputOption(path=str(output_path or (tmpdir / "out.txt"))),
        template=TemplateOption(folder=str(template_dir), file="test.tpl"),
        read_content=None,
        parse=parse,
        variables=None,
        additional_params=None,
    )
    config = Config(version="1.0", name="test", recipes=[recipe], presets=[])
    return config, recipe


@pytest.mark.parametrize(
    "template_content,input_name,input_content,output_name,expected",
    [
        ("Hello {{ name }}", "input.txt", "dummy", "out.txt", "Hello"),
        ("{{ variables.fileName }}", "input.txt", "dummy", "out.txt", "input.txt"),
        ("{{ content }}", "input.txt", "abc123", "out.txt", "abc123"),
        ("ok", "sample.txt", "dummy", "sample.txt.out", "ok"),
    ],
)
def test_run_recipe_param(
    template_content, input_name, input_content, output_name, expected
):
    tmpdir = Path(tempfile.mkdtemp())
    try:
        infile = tmpdir / input_name
        infile.write_text(input_content, encoding="utf-8")
        config, recipe = make_config_and_recipe(
            tmpdir, template_content=template_content
        )
        if output_name != "out.txt":
            recipe.output.path = str(tmpdir / output_name)
        run_recipe(infile, recipe, config)
        out = (tmpdir / output_name).read_text(encoding="utf-8")
        assert expected in out
    finally:
        shutil.rmtree(tmpdir)


def test_run_recipe_template_folder_not_exist():
    tmpdir = Path(tempfile.mkdtemp())
    try:
        infile = tmpdir / "input.txt"
        infile.write_text("dummy", encoding="utf-8")
        recipe = RecipeOption(
            enabled=True,
            id="r1",
            name="TestRecipe",
            input=InputOption(file_pattern="*.txt"),
            output=OutputOption(path=str(tmpdir / "out.txt")),
            template=TemplateOption(folder=str(tmpdir / "not_exist"), file="test.tpl"),
            read_content=None,
            parse=None,
            variables=None,
            additional_params=None,
        )
        config = Config(version="1.0", name="test", recipes=[recipe], presets=[])
        run_recipe(infile, recipe, config)
        assert not (tmpdir / "out.txt").exists()
    finally:
        shutil.rmtree(tmpdir)


@pytest.mark.parametrize(
    "parse_type,parse_options,input_content,expected,template_content",
    [
        ("plain", None, "abc", "abc", "{{ parse_result }}"),
        ("json", None, json.dumps({"foo": "bar"}), "bar", "{{ parse_result['foo'] }}"),
        ("yaml", None, "foo: bar", "bar", "{{ parse_result['foo'] }}"),
        (
            "xml",
            None,
            "<root><foo>bar</foo></root>",
            "bar",
            "{{ parse_result['root']['foo']['#text'] }}",
        ),
        ("dsv", DsvOption(), "a\tb\nabc\t123", "abc", "{{ parse_result[0]['a'] }}"),
    ],
)
def test_run_recipe_parse_types(
    parse_type, parse_options, input_content, expected, template_content
):
    tmpdir = Path(tempfile.mkdtemp())
    try:
        infile = tmpdir / "input.txt"
        infile.write_text(input_content, encoding="utf-8")
        parse = ParseOption(
            parse_type=parse_type,
            parse_result_name="parse_result",
            dsv_options=parse_options if parse_type == "dsv" else None,
            json_options=None,
            yaml_options=None,
            xml_options=None,
            textfsm_options=None,
        )
        config, recipe = make_config_and_recipe(
            tmpdir, template_content=template_content, parse=parse
        )
        run_recipe(infile, recipe, config)
        out = (tmpdir / "out.txt").read_text(encoding="utf-8")
        assert expected in out
    finally:
        shutil.rmtree(tmpdir)


def test_run_recipe_output_placeholder():
    tmpdir = Path(tempfile.mkdtemp())
    try:
        infile = tmpdir / "input.txt"
        infile.write_text("dummy", encoding="utf-8")
        config, recipe = make_config_and_recipe(
            tmpdir, template_content="ok", output_path=tmpdir / "${fileName}.out"
        )
        run_recipe(infile, recipe, config)
        assert (tmpdir / "input.txt.out").exists()
    finally:
        shutil.rmtree(tmpdir)
