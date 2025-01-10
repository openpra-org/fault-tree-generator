import xml.etree.ElementTree as ET
import xml.dom.minidom
import html
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class XMLDumper:
    def __init__(self, name, event_tree_name):
        self.name = name
        self.event_tree_name = event_tree_name
        self.fault_tree_name_list = []
        self.fault_tree_logic_list = []
        self.model_data_list = []
        logging.info(f"Initialized XMLDumper with name: {self.name} and event_tree_name: {self.event_tree_name}")

    def dump_object_to_xml(self, generated_objects, file_path):
        try:
            logging.info(f"Starting XML dump to file: {file_path}")
            # Create a root element for the XML tree
            root = ET.Element('opsa-mef')
            initating_event_element = ET.SubElement(root, 'define-initiating-event', {'name': self.name, 'event-tree': self.event_tree_name})

            # Append each parsed object (XML element) to the root
            if isinstance(generated_objects, (list, tuple)):
                for generated_object in generated_objects:
                    root.append(generated_object)
                    logging.debug(f"Added generated object to root: {generated_object.tag}")
            else:
                root.append(generated_objects)
                logging.debug(f"Added generated object to root: {generated_objects.tag}")

            # Adding fault tree logic
            for fault_tree_content in self.fault_tree_logic_list:
                # Fault tree content may be a string, so we need to convert it to an XML element
                if isinstance(fault_tree_content, str):
                    fault_tree_content = ET.fromstring(fault_tree_content)
                logging.debug(f"Adding Fault Tree Content to XML: {fault_tree_content.tag}")
                root.append(fault_tree_content)

            # Adding model data
            for model_data in self.model_data_list:
                if isinstance(model_data, str):
                    model_data = ET.fromstring(model_data)
                logging.debug(f"Adding Model Data to XML: {model_data.tag}")
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
                logging.info(f"XML file successfully written to: {file_path}")

        except Exception as e:
            logging.error(f"Error dumping XML object to file {file_path}: {e}")
