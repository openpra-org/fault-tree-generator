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
    def _build_initial_state_xml(self, state, parent_element):
        queue = deque([(state, parent_element)])  # Initialize a queue with the root element
        processed_elements = set()  # Track processed elements to avoid duplication

        while queue:
            current_state, current_parent = queue.popleft()  # Dequeue the current element

            # Check if the current_state has already been processed
            if id(current_state) in processed_elements:
                continue  # Skip processing if the element has already been processed
            processed_elements.add(id(current_state))

            # Ensure the state dictionary has the 'name' key
            state_name = current_state.get('name', 'unknown_element')
            # Create the current element with its attributes
            current_element = ET.SubElement(current_parent, state_name, current_state.get('attributes', {}))

            # Iterate over the children of the current state
            for child in current_state.get('children', []):
                # Enqueue child elements for processing
                queue.append((child, current_element))