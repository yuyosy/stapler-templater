import xml.etree.ElementTree as ET

from config import XmlOption


def _etree_to_dict(elem):
    d = {elem.tag: {} if elem.attrib else None}
    children = list(elem)
    if children:
        dd = {}
        for dc in map(_etree_to_dict, children):
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
        t.update(("@" + k, v) for k, v in elem.attrib.items())
        d[elem.tag] = t
    text = (elem.text or "").strip()
    if text:
        t = d[elem.tag]
        if t is None:
            t = {}
        t["#text"] = text
        d[elem.tag] = t
    return d


def parse_xml(content: str, options: XmlOption | None):
    try:
        root = ET.fromstring(content)
        return _etree_to_dict(root)
    except Exception:
        return None
