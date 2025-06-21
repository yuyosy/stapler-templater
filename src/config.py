from typing import List, Literal

from pydantic import BaseModel, model_validator


class InputOption(BaseModel):
    file_pattern: str


class OutputOption(BaseModel):
    path: str
    encoding: str = "utf-8"
    write_mode: Literal["w", "a"] = "w"


class TemplateOption(BaseModel):
    folder: str
    file: str
    encoding: str = "utf-8"


class ReadContentExtractOption(BaseModel):
    extract_type: Literal["auto", "index", "line", "exact", "regex"]
    extract: str | int

    @model_validator(mode="after")
    def check_extract_type(self):
        if self.extract_type in ["index", "line"] and not isinstance(self.extract, int):
            raise ValueError(
                f"For '{self.extract_type}' extract_type, 'extract' must be an integer."
            )
        elif self.extract_type in ["exact", "regex"] and not isinstance(
            self.extract, str
        ):
            raise ValueError(
                f"For '{self.extract_type}' extract_type, 'extract' must be a string."
            )
        return self


class ReadContentOption(BaseModel):
    start: ReadContentExtractOption | None = None
    end: ReadContentExtractOption | None = None
    encoding: str = "utf-8"


class JsonOption(BaseModel):
    pass


class YamlOption(BaseModel):
    pass


class XmlOption(BaseModel):
    pass


class DsvOption(BaseModel):
    parse_type: Literal["list", "dict"] = "dict"
    enable_header: bool = True
    delimiter: str = "\t"
    skip_empty_lines: bool = True
    comment_line: str | None = None


class TextFSMOption(BaseModel):
    parse_type: Literal["list", "dict"] = "dict"
    enable_header: bool = True
    template: str
    encoding: str = "utf-8"


class ParseOption(BaseModel):
    parse_type: Literal["plain", "json", "yaml", "xml", "dsv", "textfsm"]
    parse_result_name: str = "parse_result"
    json_options: JsonOption | None = None
    yaml_options: YamlOption | None = None
    xml_options: XmlOption | None = None
    dsv_options: DsvOption | None = None
    textfsm_options: TextFSMOption | None = None

    @model_validator(mode="after")
    def check_textfsm_required(self):
        if self.parse_type == "textfsm" and self.textfsm_options is None:
            raise ValueError("textfsm_options is required when parse_type is 'textfsm'")
        return self


class VariableOption(BaseModel):
    target: Literal["filename", "filepath", "content"]
    pattern: str


class AdditionalParamOption(BaseModel):
    value: str


class RecipeOption(BaseModel):
    enabled: bool
    id: str
    name: str
    input: InputOption
    output: OutputOption
    template: TemplateOption
    read_content: ReadContentOption | None = None
    parse: ParseOption | None = None
    variables: dict[str, VariableOption] | None = None
    additional_params: dict[str, str | AdditionalParamOption] | None = None


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
