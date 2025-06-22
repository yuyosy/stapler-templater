import shutil
import tempfile
from pathlib import Path

import pytest

from src.config import (
    Config,
    InputOption,
    OutputOption,
    PresetOption,
    PresetRecipeOption,
    RecipeOption,
    TemplateOption,
)
from src.processor.runner import run_processor


def make_config(tmpdir, enabled=True):
    template_dir = tmpdir / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "test.tpl").write_text("ok", encoding="utf-8")
    recipe = RecipeOption(
        enabled=enabled,
        id="r1",
        name="TestRecipe",
        input=InputOption(file_pattern="*.txt"),
        output=OutputOption(path=str(tmpdir / "out.txt")),
        template=TemplateOption(folder=str(template_dir), file="test.tpl"),
        read_content=None,
        parse=None,
        variables=None,
        additional_params=None,
    )
    preset = PresetOption(
        enabled=enabled,
        id="Preset1",
        name="Preset1",
        recipes=[PresetRecipeOption(recipe="r1", enabled=enabled)],
    )
    return Config(version="1.0", name="test", recipes=[recipe], presets=[preset])


@pytest.mark.parametrize(
    "recipes,presets,should_exist",
    [
        (["r1"], None, True),
        (None, ["Preset1"], True),
        (None, None, False),
        (["r1"], None, False),  # disabled recipe
        (None, ["Preset1"], False),  # disabled preset
    ],
)
def test_run_processor_param(recipes, presets, should_exist):
    tmpdir = Path(tempfile.mkdtemp())
    try:
        infile = tmpdir / "input.txt"
        infile.write_text("dummy", encoding="utf-8")
        enabled = should_exist if (recipes or presets) and should_exist else False
        config = make_config(tmpdir, enabled=enabled)
        run_processor(infile, config, recipes=recipes, presets=presets)
        exists = (tmpdir / "out.txt").exists()
        assert exists == should_exist
    finally:
        shutil.rmtree(tmpdir)
