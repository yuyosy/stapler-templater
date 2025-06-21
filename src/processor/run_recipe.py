from pathlib import Path
from typing import Any, Iterator

from loguru import logger
from pydantic import BaseModel

from config import Config, InputOption, OutputOption, RecipeOption
from processor.parser.dsv_parser import parse_dsv
from processor.parser.json_parser import parse_json
from processor.parser.textfsm_parser import parse_textfsm
from processor.parser.xml_parser import parse_xml
from processor.parser.yaml_parser import parse_yaml
from processor.read_content import read_content
from processor.templater import setup_template_environment
from utilities.resolve_path import resolve_path


class RecipeParams(BaseModel):
    content: str = ""
    parse_result: Any = None
    result_name: str = "parse_result"

    def to_dict(self):
        d = {"content": self.content}
        if self.parse_result is not None:
            d[self.result_name] = self.parse_result
        return d


def run_recipe(
    input_path: Path,
    recipe: RecipeOption,
    config: Config,
):
    logger.info(f"Processing {recipe.id}({recipe.name}):  {input_path}")

    template_env = setup_template_environment(recipe.template)
    if not template_env:
        logger.error(f"Failed to set up template environment for recipe: {recipe.id}")
        return

    for file in iter_files(input_path, recipe.input):
        if not file:
            logger.error(f"No valid files found in input path: {input_path}")
            continue
        logger.info(f"Processing file: {file}")
        params = RecipeParams()
        params.content = read_content(file, recipe.read_content)

        if recipe.parse:
            match recipe.parse.parse_type:
                case "plain":
                    result = params.content
                case "json":
                    result = parse_json(params.content, recipe.parse.json_options)
                case "yaml":
                    result = parse_yaml(params.content, recipe.parse.yaml_options)
                case "xml":
                    result = parse_xml(params.content, recipe.parse.xml_options)
                case "dsv":
                    result = parse_dsv(params.content, recipe.parse.dsv_options)
                case "textfsm":
                    result = parse_textfsm(params.content, recipe.parse.textfsm_options)
                case _:
                    logger.error(f"Unsupported parse type: {recipe.parse.parse_type}")
                    result = {}
            params.parse_result = result
            if recipe.parse.parse_result_name:
                params.result_name = recipe.parse.parse_result_name
        renderer = template_env.get_template(recipe.template.file)
        rendered = renderer.render(params.to_dict())
        write_output(rendered, recipe.output, params)


def iter_files(input_path: Path, option: InputOption) -> Iterator[Path]:
    if input_path.is_file():
        yield resolve_path(input_path)
    elif input_path.is_dir():
        for file in input_path.glob(option.file_pattern):
            if not file.is_file():
                continue
            yield resolve_path(file)
    logger.error(f"Invalid input path: {input_path}")


def write_output(rendered: str, option: OutputOption, params: RecipeParams):
    output_path = resolve_path(replace_placeholders(option.path))
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open(option.write_mode, encoding=option.encoding) as f:
        f.write(rendered)
    logger.info(f"Output written to [{option.write_mode}] {output_path}")


def replace_placeholders(template: str) -> str:
    return template
