from ordered_set import OrderedSet
from typing import Optional, TYPE_CHECKING, Set
from pyeda.inter import *

# Use TYPE_CHECKING to avoid circular imports at runtime but still enable type hinting.
if TYPE_CHECKING:
    from .gate import Gate


class Event:
    """Representation of a base class for an event in a fault tree.

    An event can be a basic event, an intermediate event, or a top-level event in the fault tree.
    It can have multiple parents representing the gates it is connected to.

    Attributes:
        name (str): A unique identifier for the event.
        parents (OrderedSet[Gate]): A set of parent gates that this event is connected to.
    """

    def __init__(self, name: Optional[str] = None):
        """Initializes a new Event with a unique name.

        Note that the tracking of parents introduces a cyclic reference, which is
        why the parents are stored in an OrderedSet to prevent duplicates.

        Args:
            name (Optional[str]): Identifier for the event. Defaults to None.
        """
        self.name: Optional[str] = name
        self.parents: OrderedSet['Gate'] = OrderedSet()

    def __str__(self) -> str:
        """Returns the string representation of the event.

        Returns:
            str: The name of the event.
        """
        return self.name if self.name is not None else ''

    def expr(self) -> str:
        """Returns the boolean expression string for this event

        Returns:
            str: The name of the event.
        """
        return str(self)

    def to_bdd(self, var_order: Optional[OrderedSet[str]] = None):
        """Converts the event to a Binary Decision Diagram (BDD).

        This method should be overridden by subclasses.

        Args:
            var_order (Optional[OrderedSet[str]]): The order of variables for the BDD.

        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        raise NotImplementedError("Subclasses must override this method")

    def __hash__(self) -> int:
        """Returns the hash of the event.

        Returns:
            int: The hash of the event's name.
        """
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        """Checks equality with another event based on the name.

        Args:
            other (object): The other event to compare with.

        Returns:
            bool: True if both events have the same name, False otherwise.
        """
        if not isinstance(other, Event):
            return NotImplemented
        return self.name == other.name

    def is_common(self) -> bool:
        """Determines if this event appears in multiple parent gates.

        Returns:
            bool: True if the event has more than one parent, False otherwise.
        """
        return len(self.parents) > 1

    def is_orphan(self) -> bool:
        """Determines if the event has no parent gates.

        Returns:
            bool: True if the event has no parents, False otherwise.
        """
        return not self.parents

    def num_parents(self) -> int:
        """Returns the number of unique parent gates.

        Returns:
            int: The number of parent gates.
        """
        return len(self.parents)

    def add_parent(self, gate: 'Gate'):
        """Adds a gate as a parent of the event.

        Args:
            gate (Gate): The gate where this event appears.

        Raises:
            AssertionError: If the gate is already a parent of the event.
        """
        assert gate not in self.parents, "The gate is already a parent of this event."
        self.parents.add(gate)
