from io import StringIO

from ruamel.yaml import YAML

from config import YamlOption


def parse_yaml(content: str, options: YamlOption | None):
    yaml = YAML(typ="safe")
    try:
        return yaml.load(StringIO(content))
    except Exception:
        return None
