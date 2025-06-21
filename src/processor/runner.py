from pathlib import Path
from typing import Iterator

from loguru import logger

from config import Config, RecipeOption
from processor.run_recipe import run_recipe


def run_processor(
    input_path: Path,
    config: Config,
    recipes: list[str] | None = None,
    presets: list[str] | None = None,
):
    if not recipes and not presets:
        logger.error("At least one of 'recipes' or 'presets' must be provided.")
        return
    for recipe in iter_recipes(config, recipes, presets):
        if not recipe:
            logger.warning("No valid recipes found in the provided configuration.")
            continue
        run_recipe(input_path, recipe, config)


def iter_recipes(
    config: Config,
    recipes: list[str] | None = None,
    presets: list[str] | None = None,
) -> Iterator[RecipeOption | None]:
    if presets:
        for preset_name in presets:
            logger.info(f"Processing preset: {preset_name}")
            preset = config.get_preset(preset_name)
            if not preset:
                logger.warning(f"Preset '{preset_name}' not found in config.")
                continue
            if not preset.enabled:
                logger.warning(f"Preset '{preset_name}' is not enabled.")
                continue
            for recipe_id in preset.get_enabled_recipes():
                recipe = config.get_recipe(recipe_id)
                if not recipe:
                    logger.warning(f"Recipe '{recipe_id}' not found in config.")
                    continue
                if not recipe.enabled:
                    logger.warning(f"Recipe '{recipe_id}' is not enabled.")
                    continue
                yield recipe

    if recipes:
        for recipe_id in recipes:
            recipe = config.get_recipe(recipe_id)
            if not recipe:
                logger.warning(f"Recipe '{recipe_id}' not found in config.")
                continue
            if not recipe.enabled:
                logger.warning(f"Recipe '{recipe_id}' is not enabled.")
                continue
            yield recipe
