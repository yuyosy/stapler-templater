import xml.etree.ElementTree as ET
from typing import Any, Dict

from config import XmlOption


def _etree_to_dict(elem, attribute_key, text_key) -> dict:
    d: Dict[str, Any] = {elem.tag: {} if elem.attrib else None}
    children = list(elem)
    if children:
        dd: Dict[str, Any] = {}
        for child in children:
            dc = _etree_to_dict(child, attribute_key, text_key)
            if not isinstance(dc, dict):
                continue
            for k, v in dc.items():
                if k in dd:
                    if not isinstance(dd[k], list):
                        dd[k] = [dd[k]]
                    dd[k].append(v)
                else:
                    dd[k] = v
        d = {elem.tag: dd}
    if elem.attrib:
        t = d[elem.tag]
        if t is None:
            t = {}
        t.update((attribute_key.format(key=k), v) for k, v in elem.attrib.items())
        d[elem.tag] = t
    text = (elem.text or "").strip()
    if text:
        t = d[elem.tag]
        if t is None:
            t = {}
        t[text_key] = text
        d[elem.tag] = t
    return d


def parse_xml(content: str, options: XmlOption | None):
    try:
        root = ET.fromstring(content)
        if options is not None:
            attribute_key = options.attribute_key
            text_key = options.text_key
        else:
            attribute_key = "@{key}"
            text_key = "#text"
        return _etree_to_dict(root, attribute_key, text_key)
    except Exception:
        return None
