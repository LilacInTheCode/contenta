from typing import overload
from xml.etree.ElementTree import Element


class CSCRElement(Element):
    def __init__(self, tag: str, attributes: dict[str, str] | None = None):
        if attributes is None: attributes = dict()
        super().__init__(tag, attributes)

    @classmethod
    def validate(cls, data: dict[str, str]) -> Element | None:
        """For child classes to implement their own data validation"""
        return None


class ClipElement(CSCRElement):
    def __init__(self):
        super().__init__("clip")

    @classmethod
    def validate(cls, data: dict[str, str]) -> Element | None:
        # Title of the clip goes in between the tags
        title = data.pop("title", "untitled clip")
        start = data.get("start", None)
        end = data.get("end", None)
        if start is None or end is None:
            return None

        new_element = cls()
        new_element.text = title

        new_element.attrib.update(data)

        return new_element
