from pathlib import Path
from typing import Any

import regex
from loguru import logger

from config import RecipeOption


def resolve_recipe_variables(
    file: Path, content: str, recipe: RecipeOption
) -> dict[str, Any]:
    def _get_path(path: Path, path_separator: str) -> str:
        if path_separator == "posix":
            return str(path.as_posix())
        else:
            return str(path)

    variables = {
        "fileName": file.name,
        "fileExt": file.suffix,
        "filePath": str(file),
        "parentName": file.parent.name,
        "parentPath": str(file.parent),
        "templateName": recipe.template.file,
        "templateFolder": recipe.template.folder,
    }

    if recipe.variables and recipe.variables.presets_overwrite:
        for key, value in recipe.variables.presets_overwrite.items():
            if key not in variables:
                continue
            match key:
                case "filePath":
                    variables[key] = _get_path(file, value.path_separator)
                case "parentPath":
                    variables[key] = _get_path(file.parent, value.path_separator)
                case _:
                    continue

    if not recipe.variables or not recipe.variables.defined:
        return variables
    for key, param in recipe.variables.defined.items():
        match param.target:
            case "filename":
                target = file.name
            case "filepath":
                target = _get_path(file, param.path_separator)
            case "content":
                target = content
            case _:
                logger.warning(f"Unknown variable target: {param.target}")
                continue
        pattern = regex.compile(param.pattern)
        match = pattern.search(target)
        if match:
            if isinstance(param.match_index, int):
                index = (
                    param.match_index
                    if param.match_index > 0
                    and param.match_index <= len(match.groups())
                    else 0
                )
            else:
                index = (
                    param.match_index if param.match_index in match.groupdict() else 0
                )
            variables[key] = match.group(index)
        else:
            variables[key] = ""

    return variables
