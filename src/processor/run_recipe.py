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
from processor.recipe_variables import resolve_recipe_variables
from processor.templater import setup_template_environment
from utilities.resolve_path import resolve_path


class RecipeParams(BaseModel):
    content: str = ""
    parse_result: Any = None
    variables: dict[str, Any] = {}
    result_name: str = "parse_result"

    def to_dict(self):
        d = {"content": self.content, "variables": self.variables}
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
        params = create_recipe_params(file, recipe)
        params.variables = resolve_recipe_variables(file, params.content, recipe)
        rendered = render_template(template_env, recipe.template.file, params)
        write_output(rendered, recipe.output, params)


def create_recipe_params(file: Path, recipe: RecipeOption) -> RecipeParams:
    params = RecipeParams()
    params.content = read_content(file, recipe.read_content)
    if recipe.parse:
        params.parse_result, params.result_name = parse_content(
            params.content, recipe.parse
        )
    return params


def parse_content(content: str, parse_option) -> tuple[Any, str]:
    parse_type = parse_option.parse_type
    result_name = parse_option.parse_result_name or "parse_result"
    match parse_type:
        case "plain":
            result = content
        case "json":
            result = parse_json(content, parse_option.json_options)
        case "yaml":
            result = parse_yaml(content, parse_option.yaml_options)
        case "xml":
            result = parse_xml(content, parse_option.xml_options)
        case "dsv":
            result = parse_dsv(content, parse_option.dsv_options)
        case "textfsm":
            result = parse_textfsm(content, parse_option.textfsm_options)
        case _:
            logger.error(f"Unsupported parse type: {parse_type}")
            result = {}
    return result, result_name


def render_template(template_env, template_file: str, params: RecipeParams) -> str:
    renderer = template_env.get_template(template_file)
    return renderer.render(params.to_dict())


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
    output_path = resolve_path(replace_placeholders(option.path, params.variables))
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open(option.write_mode, encoding=option.encoding) as f:
        f.write(rendered)
    logger.info(f"Output written to [{option.write_mode}] {output_path}")


def replace_placeholders(template: str, variables: dict[str, Any]) -> str:
    for key, value in variables.items():
        template = template.replace("${" + key + "}", str(value))
    return template
