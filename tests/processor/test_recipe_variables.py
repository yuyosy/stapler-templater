from pathlib import Path

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


def test_resolve_recipe_variables_filename():
    file = Path("/tmp/sample_123.txt")
    content = "abc content"
    variables = VariablesOption(
        defined={"num": VariableOption(target="filename", pattern=r"\d+")}
    )
    recipe = make_recipe("tmpl.txt", "tmpl_dir", variables)
    result = resolve_recipe_variables(file, content, recipe)
    assert result["num"] == "123"


def test_resolve_recipe_variables_filepath():
    file = Path("/tmp/123/parent/abc_789.txt")
    content = "xyz content"
    variables = VariablesOption(
        defined={"val": VariableOption(target="filepath", pattern=r"\d+.*\.txt")}
    )
    recipe = make_recipe("tmpl.txt", "tmpl_dir", variables)
    result = resolve_recipe_variables(file, content, recipe)
    assert result["val"] == "123/parent/abc_789.txt"


def test_resolve_recipe_variables_content():
    file = Path("/tmp/irrelevant.txt")
    content = "abc=xyz; id=456;"
    variables = VariablesOption(
        defined={"id": VariableOption(target="content", pattern=r"id=\d+")}
    )
    recipe = make_recipe("tmpl.txt", "tmpl_dir", variables)
    result = resolve_recipe_variables(file, content, recipe)
    assert result["id"] == "id=456"


def test_resolve_recipe_variables_no_match():
    file = Path("/tmp/abc.txt")
    content = "no match here"
    variables = VariablesOption(
        defined={"notfound": VariableOption(target="content", pattern=r"zzz=(\d+)")}
    )
    recipe = make_recipe("tmpl.txt", "tmpl_dir", variables)
    result = resolve_recipe_variables(file, content, recipe)
    assert result["notfound"] == ""


def test_resolve_recipe_variables_match_index():
    file = Path("/tmp/abc.txt")
    content = "abc=123; xyz=456;"
    variables = VariablesOption(
        defined={
            "both": VariableOption(
                target="content", pattern=r"(abc)=(123)", match_index=2
            )
        }
    )
    recipe = make_recipe("tmpl.txt", "tmpl_dir", variables)
    result = resolve_recipe_variables(file, content, recipe)
    assert result["both"] == "123"


def test_resolve_recipe_variables_match_index_named_group():
    file = Path("/tmp/abc.txt")
    content = "abc=123; xyz=456;"
    variables = VariablesOption(
        defined={
            "named": VariableOption(
                target="content", pattern=r"abc=(?P<id>\d+)", match_index="id"
            )
        }
    )
    recipe = make_recipe("tmpl.txt", "tmpl_dir", variables)
    result = resolve_recipe_variables(file, content, recipe)
    assert result["named"] == "123"


def test_resolve_recipe_variables_no_variables():
    file = Path("/tmp/abc.txt")
    content = "abc=123"
    recipe = make_recipe("tmpl.txt", "tmpl_dir", None)
    result = resolve_recipe_variables(file, content, recipe)
    assert result["fileName"] == "abc.txt"
    assert result["templateName"] == "tmpl.txt"
    assert result["templateFolder"] == "tmpl_dir"
