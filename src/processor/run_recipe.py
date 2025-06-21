from pathlib import Path

from loguru import logger

from config import Config, RecipeOption


def run_recipe(
    input_path: Path,
    recipe: RecipeOption,
    config: Config,
):
    logger.info(f"Processing {recipe.id}({recipe.name}):  {input_path}")
