from typing import List, Literal

from pydantic import BaseModel


class InputOption(BaseModel):
    file_pattern: str
    encoding: str = "utf-8"


class OutputOption(BaseModel):
    path: str
    encoding: str = "utf-8"
    write_mode: Literal["w", "a"] = "w"


class TemplateOption(BaseModel):
    folder: str
    file: str


class RecipeOption(BaseModel):
    enabled: bool
    id: str
    name: str
    input: InputOption
    output: OutputOption
    template: TemplateOption


class PresetRecipeOption(BaseModel):
    recipe: str
    enabled: bool


class PresetOption(BaseModel):
    enabled: bool
    id: str
    name: str
    recipes: List[PresetRecipeOption]

    def has_recipe(self, recipe_id: str) -> bool:
        return any(recipe.recipe == recipe_id for recipe in self.recipes)

    def get_enabled_recipes(self) -> List[str]:
        return [recipe.recipe for recipe in self.recipes if recipe.enabled]

    def get_recipe(self, recipe_id: str) -> PresetRecipeOption | None:
        for recipe in self.recipes:
            if recipe.recipe == recipe_id:
                return recipe
        return None


class Config(BaseModel):
    version: str
    name: str
    recipes: List[RecipeOption]
    presets: List[PresetOption]

    def has_recipe(self, recipe_id: str) -> bool:
        return any(recipe.id == recipe_id for recipe in self.recipes)

    def has_preset(self, preset_name: str) -> bool:
        return any(preset.name == preset_name for preset in self.presets)

    def get_enabled_recipes(self) -> List[str]:
        return [recipe.id for recipe in self.recipes if recipe.enabled]

    def get_enabled_presets(self) -> List[str]:
        return [preset.name for preset in self.presets if preset.enabled]

    def get_recipe(self, recipe_id: str) -> RecipeOption | None:
        for recipe in self.recipes:
            if recipe.id == recipe_id:
                return recipe
        return None

    def get_preset(self, preset_id: str) -> PresetOption | None:
        for preset in self.presets:
            if preset.id == preset_id:
                return preset
        return None
