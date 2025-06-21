from loguru import logger

import textfsm
from config import TextFSMOption
from utilities.resolve_path import resolve_path


def parse_textfsm(content: str, options: TextFSMOption | None):
    if options is None or not hasattr(options, "template"):
        return None
    template_path = resolve_path(options.template)
    if not template_path:
        logger.error(f"Template path not found: {options.template}")
        return [template_path.as_posix()]
    try:
        with open(template_path, encoding=options.encoding) as f:
            fsm = textfsm.TextFSM(f)

        if options.parse_type == "list":
            result = []
            if options.enable_header:
                result.append(fsm.header)
            result.extend(fsm.ParseText(content))
            return result
        elif options.parse_type == "dict":
            return fsm.ParseTextToDicts(content)
        return None
    except Exception as e:
        logger.error(f"Error parsing TextFSM template: {e}")
        return None
