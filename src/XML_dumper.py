import xml.etree.ElementTree as ET
import xml.dom.minidom
import html

class XMLDumper:
    def __init__(self, name, event_tree_name):
        self.name = name
        self.event_tree_name = event_tree_name
        self.fault_tree_name_list = []
        self.fault_tree_logic_list =[]
        self.model_data_list = []

    def dump_object_to_xml(self, generated_objects, file_path):
        try:
            # Create a root element for the XML tree
            root = ET.Element('opsa-mef')
            initating_event_element= ET.SubElement(root, 'define-initiating-event', {'name':self.name, 'event-tree':self.event_tree_name})

            # Append each parsed object (XML element) to the root
            if isinstance(generated_objects, (list, tuple)):
                for generated_object in generated_objects:
                    root.append(generated_object)
            else:
                root.append(generated_objects)

            for fault_tree_content in self.fault_tree_logic_list:
                # Fault tree content may be a string, so we need to convert it to an XML element
                if isinstance(fault_tree_content, str):
                    fault_tree_content = ET.fromstring(fault_tree_content)
                print(f'Fault Tree Content in XML Dumper Loop ==={fault_tree_content}')
                root.append(fault_tree_content)

            for model_data in self.model_data_list:
                if isinstance(model_data, str):
                    model_data = ET.fromstring(model_data)
                print(f'Fault Tree Content in XML Dumper Loop ==={model_data}')
                root.append(model_data)


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
