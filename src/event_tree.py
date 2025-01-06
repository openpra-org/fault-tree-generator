import xml.etree.ElementTree as ET
from collections import deque
from xml.sax.saxutils import escape

class EventTree:
    def __init__(self, name):
        self.name = name
        self.functional_events_id = []
        self.functional_events_name =[]
        self.sequences = []
        self.initial_state = {}

    def to_xml(self):

        event_tree_element = ET.Element('define-event-tree', {'name': self.name})

        # Iterate over both functional events and their corresponding labels
        for functional_event, functional_event_name in zip(self.functional_events_id, self.functional_events_name):
            # Create the functional event element with the corresponding label
            functional_event_element = ET.SubElement(event_tree_element, 'define-functional-event',
                                                     {'name': functional_event})
            label_element = ET.SubElement(functional_event_element, 'label')
            label_element.text = escape(functional_event_name)  # Set label text from the corresponding name list

        for sequence in self.sequences:
            sequence_element = ET.SubElement(event_tree_element, 'define-sequence', {'name': sequence})

        if self.initial_state:
            initial_state_element = ET.SubElement(event_tree_element, 'initial-state')
            self._build_initial_state_xml(self.initial_state, initial_state_element)

        return event_tree_element

    def _build_initial_state_xml(self, parent_element):
        """
        Build the initial state structure for the event tree in XML.

        Args:
            parent_element (Element): The parent XML element to which child elements will be added.
        """

        def recursive_build(parent, depth):
            # Stop recursion when all functional events are processed
            if depth >= len(self.functional_events_id):
                return

            # Get the current functional event ID and name
            functional_event_id = self.functional_events_id[depth]

            # Create a fork element for the current functional event
            fork_element = ET.SubElement(parent, 'fork', {'functional-event': functional_event_id})

            # Create Success path
            success_path = ET.SubElement(fork_element, 'path', {'state': 'Success'})
            success_formula = ET.SubElement(success_path, 'collect-formula')
            not_element = ET.SubElement(success_formula, 'not')
            ET.SubElement(not_element, 'gate', {'name': f'FT{depth + 1}.TOP'})
            if depth == len(self.functional_events_id) - 1:  # If it's the last event
                ET.SubElement(success_path, 'sequence', {'name': f'S{2 ** (depth + 1) - 1}'})
            else:
                recursive_build(success_path, depth + 1)

            # Create Failure path
            failure_path = ET.SubElement(fork_element, 'path', {'state': 'Failure'})
            failure_formula = ET.SubElement(failure_path, 'collect-formula')
            ET.SubElement(failure_formula, 'gate', {'name': f'FT{depth + 1}.TOP'})
            if depth == len(self.functional_events_id) - 1:  # If it's the last event
                ET.SubElement(failure_path, 'sequence', {'name': f'S{2 ** (depth + 1) - 2}'})
            else:
                recursive_build(failure_path, depth + 1)

        # Start recursive building from the root element
        recursive_build(parent_element, 0)
