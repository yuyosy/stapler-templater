import sys
from pathlib import Path

from loguru import logger
from pydantic import ValidationError
from ruamel.yaml import YAML

from args import set_parser
from config import Config
from processor.runner import run_processor
from utilities.resolve_path import resolve_path


def get_config(config_path: Path) -> Config | None:
    with config_path.open("r", encoding="utf-8") as f:
        config_data = YAML().load(f)
    try:
        return Config(**config_data)
    except ValidationError as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return None


def main():
    parser, args = set_parser()
    logger.remove()
    logger.add(sys.stderr, level="DEBUG" if args.verbose else "INFO")

    config = get_config(resolve_path(args.config))
    if not config:
        parser.error(f"Invalid configuration file: {args.config}")
        parser.exit(1)
    logger.debug(config)

    logger.debug(
        f"Input Path: {resolve_path(args.input) if args.input else 'Not provided'}"
    )
    logger.debug(f"Recipes: {args.recipes if args.recipes else 'None'}")
    logger.debug(f"Presets: {args.presets if args.presets else 'None'}")

    if not args.recipes and not args.presets:
        parser.error("At least one of --recipes or --presets must be provided.")
        parser.exit(1)

    if args.input:
        input_path = resolve_path(args.input)
    else:
        input_path = resolve_path(input("Enter input path>> "))

    if not input_path.exists():
        parser.error(f"The input path '{input_path}' does not exist.")
        parser.exit(1)

    run_processor(
        input_path=input_path,
        config=config,
        recipes=args.recipes,
        presets=args.presets,
    )


if __name__ == "__main__":
    main()
