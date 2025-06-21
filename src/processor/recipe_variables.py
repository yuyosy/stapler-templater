from pathlib import Path
from typing import Any

import regex
from loguru import logger

from config import RecipeOption


def resolve_recipe_variables(
    file: Path, content: str, recipe: RecipeOption
) -> dict[str, Any]:
    variables = {
        "fileName": file.name,
        "parentPath": str(file.parent),
        "parentName": file.parent.name,
        "filePath": str(file),
        "templateName": recipe.template.file,
        "templateFolder": recipe.template.folder,
    }
    if not recipe.variables:
        return variables
    for key, param in recipe.variables.items():
        match param.target:
            case "filename":
                target = file.name
            case "filepath":
                target = str(file.absolute())
            case "content":
                target = content
            case _:
                logger.warning(f"Unknown variable target: {param.target}")
                continue
        pattern = regex.compile(param.pattern)
        match = pattern.search(target)
        if match:
            index = (
                param.match_index
                if param.match_index > 0 and param.match_index < len(match.groups())
                else 0
            )
            variables[key] = match.group(index)
        else:
            variables[key] = ""

    return variables
