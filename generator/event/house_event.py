from generator.event.Event import Event


class HouseEvent(Event):
    """Representation of a house event in a fault tree.

    Attributes:
        state: State of the house event ("true" or "false").
    """

    def __init__(self, name, state):
        """Initializes a house event node.

        Args:
            name: Identifier of the node.
            state: Boolean state string of the constant.
        """
        super(HouseEvent, self).__init__(name)
        self.state = state

    def to_xml(self, printer):
        """Produces the Open-PSA MEF XML definition of the house event."""
        printer('<define-house-event name="', self.name, '">')
        printer('<constant value="', str(self.state).lower(), '"/>')
        printer('</define-house-event>')

    def to_aralia(self, printer):
        """Produces the Aralia definition of the house event."""
        printer('s(', self.name, ') = ', str(self.state).lower())
