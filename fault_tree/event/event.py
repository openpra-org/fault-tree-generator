from ordered_set import OrderedSet
from typing import Optional, TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular imports at runtime.
if TYPE_CHECKING:
    from .gate import Gate


class Event:
    """
    A base class representing an event in a fault tree analysis.

    An event can be a basic event, an intermediate event, or a top-level event in the fault tree.
    It can have multiple parents representing the gates it is connected to.

    Attributes:
        name (str): A unique identifier for the event.
        parents (OrderedSet[Gate]): A set of parent gates that this event is connected to.
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initializes an Event with a given name.

        Args:
            name (Optional[str]): The name of the event. Defaults to None.
        """
        self.name: Optional[str] = name
        self.parents: "OrderedSet[Gate]" = OrderedSet()

    def __str__(self) -> str:
        """
        Returns a string representation of the event.

        Returns:
            str: The name of the event.
        """
        return self.name if self.name is not None else ""

    def __hash__(self) -> int:
        """
        Returns the hash of the event based on its name.

        Returns:
            int: The hash of the event.
        """
        return hash(self.__str__())

    def __eq__(self, other: object) -> bool:
        """
        Checks equality with another event based on the name.

        Args:
            other (object): The other event to compare with.

        Returns:
            bool: True if both events have the same name, False otherwise.
        """
        if not isinstance(other, Event):
            return NotImplemented
        return self.name == other.name

    def is_common(self) -> bool:
        """
        Checks if the event is a common cause event in the fault tree.

        A common cause event appears in multiple places in the fault tree.

        Returns:
            bool: True if the event has more than one parent, False otherwise.
        """
        return len(self.parents) > 1

    def is_orphan(self) -> bool:
        """
        Determines if the event is an orphan, i.e., it has no parents.

        Returns:
            bool: True if the event has no parents, False otherwise.
        """
        return len(self.parents) == 0

    def num_parents(self) -> int:
        """
        Returns the number of unique parents of the event.

        Returns:
            int: The number of parent gates.
        """
        return len(self.parents)

    def add_parent(self, gate: "Gate"):
        """
        Adds a gate as a parent of the event.

        Args:
            gate (Gate): The gate to be added as a parent.

        Raises:
            AssertionError: If the gate is already a parent of the event.
        """
        assert gate not in self.parents, "The gate is already a parent of this event."
        self.parents.add(gate)
