# ~/projects/contenta/editor/cscr.py
import time
import xml.etree.ElementTree as ET
from typing import Self, Any, List, Dict
from xml.etree.ElementTree import ElementTree, Element

from PyQt6.QtCore import pyqtSignal, QObject


version = 1.0
startup_file = f"""
<cscr version=\"{version}\" id=\"cscr_root\">
    <title>Untitled</title>
    <transition desc=\"Fade In\" readable=\"_tag_desc\" />
    <monologue desc=\"Intro\" readable=\"_tag_desc_body\">
    Welcome to Contenta, the wonderful content creation tool for video essays and other scripted media.
    
    Don't mind the dust... We are still putting things into their proper places. Feel free to look around, and try to break something.
    </monologue>
    <monologue desc=\"Conclusion\" readable=\"_tag_desc_body\">
    We hope this was a rewarding experience. Please come back another time to continue your creative journey!
    </monologue>
</cscr>

"""


class CSCRTree(QObject):

    tree_updated = pyqtSignal(Element)

    def __init__(self,parent: QObject | None = None, target_version: str = f"{version}"):
        super().__init__(parent)
        self.root: Element = ET.fromstring(startup_file)
        try:
            self.validate_version(target_version)
        except ValueError as e:
            print(e)

    def index_tree(self) -> Dict[str, Element]:
        element_list = self._walk_tree(self.root)
        generated = {}
        for element in element_list:
            generated[f"{hex(id(element))[2:]}"] = element

        return generated

    @classmethod
    def from_file(cls, filepath):
        """Parses a .cscr file and populates the class."""
        instance = cls()
        try:
            instance.root = ET.parse(filepath).getroot()
        except IOError:
            return

        # Attach helpful element attributes
        for line, child in enumerate(instance.root):
            element_id = child.attrib.get("id", None)
            if element_id is None:
                child.attrib["id"] = child.tag + str(line)

        # instance.generate_content()

        return instance

    def from_input(self, input_text: str):
        """Updates the CSCR file from the text editor content."""
        pass

    def to_file(self, filepath):
        """Writes the class data to a .cscr file."""
        try:
            ElementTree(self.root).write(filepath)
        except IOError:
            pass

    def add_element(self, tag: str, content: str = "", attributes=None, parent: Element | None = None):
        """Adds or updates an element."""
        if attributes is None:
            attributes = dict()
        if parent is None:
            parent = self.root

        new_element = ET.SubElement(parent, tag, attributes)
        new_element.text = content
        for attribute, value in attributes.items():
            new_element.attrib[attribute] = value

    def drop_element(self, element_id: str):
        pass

    def get_element(self, element_id: str) -> Element | None:
        """Retrieves the content of a given tag."""
        return self.index_tree().get(element_id, None)

    def get_property(self, element_id: str, element_property: str) -> Any | None:
        element = self.get_element(element_id)
        if element is None: return None
        if element_property == "tag": return element.tag
        if element_property == "content": return element.text

        return element.attrib.get(element_property, None)

    def set_property(self, element_id: str, element_property: str, data: str):
        element = self.get_element(element_id)
        if element is None: return
        if element_property == "content":
            print(data)
            element.text = data
            return

        element.attrib[element_property] = data

    def _walk_tree(self, root: Element) -> List[Element]:
        yield root

        for child in root:
            yield from self._walk_tree(child)

    @ classmethod
    def get_readable(cls, element: Element) -> (str, str):

        # Is this content readable
        readable: str = element.attrib.get("readable", None)
        # No "readable" attribute? Skip entirely
        if readable is None: return None, None

        header_text: str = ""
        body_text: str = ""
        # "readable" attribute doesn't start with "_"? Use the attribute itself as the only readable portion
        if not readable.startswith("_"):
            body_text = f"{readable}\n"
        else:
            # Parse the "readable" tag if it has instructions for what info is readable
            text_sources: list[str] = readable[1:].split("_")
            if "tag" in text_sources:
                header_text = f"[{str(element.tag).capitalize()}]\n\n"
            if "desc" in text_sources:
                description = element.attrib.get("desc", "")
                if len(header_text) > 0:
                    header_text = f"{header_text.strip("]\n")} - {description}]\n\n"
                else:
                    header_text = f"[{description}]\n\n"
            if "body" in text_sources:
                body_text = f"{element.text}\n\n"
        return header_text, body_text

    def validate_version(self, required_version):
        """Ensures compatibility with the required version."""
        version = self.root.attrib.get("version", "0.0")
        major, minor = map(int, version.split("."))
        req_major, req_minor = map(int, required_version.split("."))
        if major < req_major or (major == req_major and minor < req_minor):
            raise ValueError(
                f"Incompatible version: {version}. Requires {required_version} or higher."
            )
