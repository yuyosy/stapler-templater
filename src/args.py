import argparse
from pathlib import Path

from pydantic import BaseModel

class Argument(BaseModel):
    config: Path = Path("config.yaml")
    input: Path | None = None
    recipes: list[str] | None = None
    presets: list[str] | None = None
    verbose: bool = False


def set_parser() -> tuple[argparse.ArgumentParser, Argument]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        metavar="<config-path>",
        default="config.yaml",
        help="Path to the configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="<input-path>",
        help="Path to the input file or directory",
    )
    parser.add_argument(
        "-r",
        "--recipes",
        type=str,
        nargs="+",
        metavar="<recipe-names>",
        help="List of recipe names to use",
    )
    parser.add_argument(
        "-p",
        "--presets",
        type=str,
        nargs="+",
        metavar="<preset-names>",
        help="List of preset names to use",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging",
    )
    return parser, Argument(**vars(parser.parse_args()))
