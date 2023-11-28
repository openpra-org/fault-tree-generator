from typing import Optional
from ordered_set import OrderedSet
from fault_tree.event import Event
from fault_tree.probability import Probability
from pyeda.inter import bddvars, expr2bdd, exprvar


class BasicEvent(Event):
    """Representation of a basic event in a fault tree.

    A basic event is a leaf node in the fault tree, representing a failure mode
    that does not depend on any other events. It is characterized by its own
    probability of occurrence.

    Attributes:
        name (str): Identifier of the basic event.
        probability (Optional[Probability]): Probability of failure of this basic event.
    """

    def __init__(self, name: str, probability: Optional[Probability] = None):
        """Initializes a BasicEvent with a name and a probability of failure.

        Inherits from the Event class and adds a probability attribute specific
        to basic events.

        Args:
            name (str): Identifier of the basic event.
            probability (Probability): An instance of Probability representing
                the likelihood of the basic event's failure.
        """
        super().__init__(name)
        self.__probability = probability

    @property
    def probability(self) -> Probability:
        """Gets the probability of failure of the basic event.

        Returns:
            Probability: The probability of failure of this basic event.
        """
        return self.__probability

    @probability.setter
    def probability(self, value: Probability):
        """Sets the probability of failure of the basic event.

        Args:
            value (Probability): The new probability of failure to be set.
        """
        if not isinstance(value, Probability) and value is not None:
            raise TypeError("probability must be an instance of Probability or None")
        self.__probability = value

    def to_bdd(self, var_order: Optional[OrderedSet[str]] = None):
        """Converts the Basic Event to a Binary Decision Diagram (BDD).

        Args:
            var_order (Optional[OrderedSet[str]]): The order of variables for the BDD.

        Returns:
            BDD: The BDD representation of the event.
        """
        if var_order is None or self.name not in var_order:
            return exprvar(self.name)
        else:
            index = var_order.index(self.name)
            return exprvar('x' + str(index))
