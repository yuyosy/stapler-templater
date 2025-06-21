import xml.etree.ElementTree as ET

from config import XmlOption


def parse_xml(content: str, options: XmlOption | None):
    try:
        return ET.fromstring(content)
    except Exception:
        return None
