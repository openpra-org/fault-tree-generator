from generator.event.Event import Event
from generator.probability import Probability


class BasicEvent(Event):
    """Representation of a basic event in a fault tree.

    Attributes:
        name:  Identifier of the node.
        probability: Probability of failure of this basic event.
    """

    def __init__(self, name: str, probability: Probability):
        """Initializes a basic event node.

        Args:
            name: Identifier of the node.
            probability: Probability of failure of this basic event.
        """
        super(BasicEvent, self).__init__(name)
        self.__probability = probability

    def to_xml(self, printer):
        """Produces the Open-PSA MEF XML definition of the basic event."""
        printer('<define-basic-event name="', self.name, '">')
        self.__probability.to_xml(printer)
        printer('</define-basic-event>')

    def to_aralia(self, printer):
        """Produces the Aralia definition of the basic event."""
        raise NotImplementedError
