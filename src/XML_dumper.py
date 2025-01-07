import xml.etree.ElementTree as ET
import xml.dom.minidom
import html

class XMLDumper:
    def __init__(self):
        pass

    def dump_object_to_xml(self, parsed_objects, file_path):
        try:
            # Create a root element for the XML tree
            root = ET.Element('opsa-mef')

            # Append each parsed object (XML element) to the root
            if isinstance(parsed_objects, (list, tuple)):
                for parsed_object in parsed_objects:
                    root.append(parsed_object)
            else:
                root.append(parsed_objects)

            # Create ElementTree object with the root element
            tree = ET.ElementTree(root)

            # Convert ElementTree to string
            xml_string = ET.tostring(root, encoding="utf-8", xml_declaration=True)

            # Parse XML string to minidom Document
            dom = xml.dom.minidom.parseString(xml_string)

            # Beautify XML
            beautified_xml = dom.toprettyxml()

            # Unescape XML entities
            unescaped_xml = html.unescape(beautified_xml)

            # Write unescaped XML to file
            with open(file_path, "w") as xml_file:
                xml_file.write(unescaped_xml)
        except Exception as e:
            print(f"Error dumping XML object to file {file_path}: {e}")

