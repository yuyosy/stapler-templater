import pytest
from pydantic import ValidationError

from src.config import (
    AdditionalParamOption,
    Config,
    InputOption,
    OutputOption,
    ParseOption,
    PresetOption,
    PresetRecipeOption,
    ReadContentExtractOption,
    RecipeOption,
    TemplateOption,
    TextFSMOption,
    VariableOption,
)


def test_input_option():
    opt = InputOption(file_pattern="*.txt")
    assert opt.file_pattern == "*.txt"


def test_output_option_defaults():
    opt = OutputOption(path="out.txt")
    assert opt.encoding == "utf-8"
    assert opt.write_mode == "w"


def test_template_option_defaults():
    opt = TemplateOption(folder="templates", file="a.tpl")
    assert opt.encoding == "utf-8"


def test_read_content_extract_option_valid():
    ReadContentExtractOption(extract_type="index", extract=1)
    ReadContentExtractOption(extract_type="line", extract=2)
    ReadContentExtractOption(extract_type="exact", extract="foo")
    ReadContentExtractOption(extract_type="regex", extract="bar")
    ReadContentExtractOption(extract_type="auto", extract="baz")


def test_read_content_extract_option_invalid():
    with pytest.raises(ValidationError):
        ReadContentExtractOption(extract_type="index", extract="notint")
    with pytest.raises(ValidationError):
        ReadContentExtractOption(extract_type="exact", extract=123)


def test_textfsm_option_defaults():
    opt = TextFSMOption(template="foo")
    assert opt.parse_type == "dict"
    assert opt.enable_header is True
    assert opt.template == "foo"


def test_parse_option_textfsm_required():
    with pytest.raises(ValidationError):
        ParseOption(parse_type="textfsm")
    # valid
    ParseOption(parse_type="textfsm", textfsm=TextFSMOption(template="foo"))


def test_variable_option():
    v = VariableOption(target="filename", pattern=".*")
    assert v.target == "filename"
    assert v.pattern == ".*"


def test_additional_param_option():
    a = AdditionalParamOption(value="bar")
    assert a.value == "bar"


def test_recipe_option():
    r = RecipeOption(
        enabled=True,
        id="r1",
        name="Recipe1",
        input=InputOption(file_pattern="*.txt"),
        output=OutputOption(path="out.txt"),
        template=TemplateOption(folder="t", file="f"),
    )
    assert r.enabled
    assert r.id == "r1"


def test_preset_option_methods():
    recipes = [
        PresetRecipeOption(recipe="r1", enabled=True),
        PresetRecipeOption(recipe="r2", enabled=False),
    ]
    preset = PresetOption(enabled=True, id="p1", name="Preset1", recipes=recipes)
    assert preset.has_recipe("r1")
    assert preset.get_enabled_recipes() == ["r1"]
    r2 = preset.get_recipe("r2")
    assert r2 is not None and r2.recipe == "r2"
    assert preset.get_recipe("notfound") is None


def test_config_methods():
    recipe = RecipeOption(
        enabled=True,
        id="r1",
        name="Recipe1",
        input=InputOption(file_pattern="*.txt"),
        output=OutputOption(path="out.txt"),
        template=TemplateOption(folder="t", file="f"),
    )
    preset = PresetOption(
        enabled=True,
        id="p1",
        name="Preset1",
        recipes=[PresetRecipeOption(recipe="r1", enabled=True)],
    )
    config = Config(version="1.0", name="C", recipes=[recipe], presets=[preset])
    assert config.has_recipe("r1")
    assert config.has_preset("Preset1")
    assert config.get_enabled_recipes() == ["r1"]
    assert config.get_enabled_presets() == ["Preset1"]
    r1 = config.get_recipe("r1")
    assert r1 is not None and r1.id == "r1"
    p1 = config.get_preset("p1")
    assert p1 is not None and p1.id == "p1"
    assert config.get_preset("notfound") is None
