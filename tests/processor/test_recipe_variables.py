from pathlib import Path

import pytest

from src.config import (
    InputOption,
    OutputOption,
    RecipeOption,
    TemplateOption,
    VariableOption,
    VariablesOption,
)
from src.processor.recipe_variables import resolve_recipe_variables


def make_recipe(template_file, template_folder, variables=None):
    template = TemplateOption(folder=template_folder, file=template_file)
    input_option = InputOption(file_pattern="*")
    output_option = OutputOption(path="dummy.txt")
    return RecipeOption(
        enabled=True,
        id="dummy",
        name="dummy",
        input=input_option,
        output=output_option,
        template=template,
        read_content=None,
        parse=None,
        variables=variables,
        additional_params=None,
    )


@pytest.mark.parametrize(
    "file,content,variables,expected",
    [
        (
            Path("/tmp/sample_123.txt"),
            "abc content",
            VariablesOption(
                defined={"num": VariableOption(target="filename", pattern=r"\d+")}
            ),
            {"num": "123"},
        ),
        (
            Path("/tmp/123/parent/abc_789.txt"),
            "xyz content",
            VariablesOption(
                defined={
                    "val": VariableOption(target="filepath", pattern=r"\d+.*\.txt")
                }
            ),
            {"val": "123/parent/abc_789.txt"},
        ),
        (
            Path("/tmp/irrelevant.txt"),
            "abc=xyz; id=456;",
            VariablesOption(
                defined={"id": VariableOption(target="content", pattern=r"id=\d+")}
            ),
            {"id": "id=456"},
        ),
        (
            Path("/tmp/abc.txt"),
            "no match here",
            VariablesOption(
                defined={
                    "notfound": VariableOption(target="content", pattern=r"zzz=(\d+)")
                }
            ),
            {"notfound": ""},
        ),
        (
            Path("/tmp/abc.txt"),
            "abc=123; xyz=456;",
            VariablesOption(
                defined={
                    "both": VariableOption(
                        target="content", pattern=r"(abc)=(123)", match_index=2
                    )
                }
            ),
            {"both": "123"},
        ),
        (
            Path("/tmp/abc.txt"),
            "abc=123; xyz=456;",
            VariablesOption(
                defined={
                    "named": VariableOption(
                        target="content", pattern=r"abc=(?P<id>\d+)", match_index="id"
                    )
                }
            ),
            {"named": "123"},
        ),
    ],
)
def test_resolve_recipe_variables_param(file, content, variables, expected):
    recipe = make_recipe("tmpl.txt", "tmpl_dir", variables)
    result = resolve_recipe_variables(file, content, recipe)
    for k, v in expected.items():
        assert result[k] == v


def test_resolve_recipe_variables_no_variables():
    file = Path("/tmp/abc.txt")
    content = "abc=123"
    recipe = make_recipe("tmpl.txt", "tmpl_dir", None)
    result = resolve_recipe_variables(file, content, recipe)
    assert result["fileName"] == "abc.txt"
    assert result["templateName"] == "tmpl.txt"
    assert result["templateFolder"] == "tmpl_dir"
