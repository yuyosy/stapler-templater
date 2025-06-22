import json

from config import JsonOption


def parse_json(content: str, _: JsonOption | None):
    try:
        return json.loads(content)
    except Exception:
        return None
