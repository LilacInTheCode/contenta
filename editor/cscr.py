# ~/projects/contenta/editor/cscr.py
import xml.etree.ElementTree as ET
import time

from xml.etree.ElementTree import ElementTree, Element, ParseError
from typing import Self, Any, Tuple, List


class CSCRFile:
    def __init__(self, version="1.0"):
        self.root: Element = Element("cscr")
        self.root.attrib["id"] = "cscr_root"
        self.root.attrib["version"] = version

        self.content: str = ""
        self.outline: dict[str, list[str] | None] | None = None
        self.section_offsets: list[tuple[str, int, int, int]] = []

    def generate_ids(self):
        """ Generate a unique id string for each existing element (may change later) """
        # serial_no: A "serial number" for this batch of IDs to prevent collisions
        serial_no = hex(int(time.time())).strip("0x")
        # Assign every tag an ID that should be unique
        for line, child in enumerate(self.root.iter()):
            child.attrib["id"] = f"_{child.tag}{serial_no}{str(line)}"

    @classmethod
    def from_empty(cls) -> Self:
        empty_file = cls()

        empty_file.add_element("title", "Untitled")
        empty_file.add_element("transition", "", { "desc": "Fade in", "readable": "_tag_desc" })
        empty_file.add_element("monologue", "Once upon a time...", { "desc": "Intro", "readable": "_tag_desc_body"})
        empty_file.generate_ids()

        empty_file.generate_content()

        return empty_file

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

        instance.generate_content()

        return instance

    def from_input(self, input_text: str):
        if self.content is None: return

        input_lines: list[str] = input_text.split("\n")
        content_lines: list[str] = self.content.split("\n")
        change_pos: int | None = None
        for line_no, line in input_lines:
            change_start: int = 0
            c_line = content_lines[line_no]
            if line == c_line:
                change_start += len(line)
                continue

            for letter_no, letter in line:
                if letter == c_line[letter_no]:
                    change_start += letter_no
                    change_pos = change_start
                    break

            if change_pos is not None: break

        self.generate_content()


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

    def get_element(self, element_id: str) -> Element | None:
        """Retrieves the content of a given tag."""
        element_list = self.root.iter()
        found_element = None
        for element in element_list:
            if element_id == element.attrib.get("id", None):
                found_element = element
                break

        return found_element

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
            element.text = data
            return

        element.attrib[element_property] = data

    def _walk_tree(self, root: Element) -> List[Element]:
        yield root

        for child in root:
            yield from self._walk_tree(child)

    def generate_outline(self):
        pass

    @classmethod
    def get_children(cls, element: Element) -> list[Element]:
        return list(element.iter())[1:]

    def generate_content(self):
        """Generates a readable representation and outline of the script."""
        self.content = ""
        rendered_text = []
        self.section_offsets.clear()
        text_position = 0

        for element in self._walk_tree(self.root):
            # Generate readable section
            element_id: str = element.attrib.get("id", None)
            if element_id is None:
                raise ParseError(f"Can't expand {element}. It is missing \"id\" attribute.")

            # Is this content readable
            readable: str = element.attrib.get("readable", None)
            # No "readable" attribute? Skip entirely
            if readable is None: continue

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
                rendered_text.append(f"{header_text}{body_text}")

                # Track offsets
                header_len = len(header_text)
                start = text_position + header_len
                end = start + len(body_text)
                self.section_offsets.append((element_id, header_len, start, end))
                text_position = end

        self.content = "".join(rendered_text)

    def validate_version(self, required_version):
        """Ensures compatibility with the required version."""
        version = self.root.attrib.get("version", "0.0")
        major, minor = map(int, version.split("."))
        req_major, req_minor = map(int, required_version.split("."))
        if major < req_major or (major == req_major and minor < req_minor):
            raise ValueError(
                f"Incompatible version: {version}. Requires {required_version} or higher."
            )
