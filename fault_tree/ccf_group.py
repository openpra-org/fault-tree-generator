from typing import Optional
from ordered_set import OrderedSet

from fault_tree.event import BasicEvent
from fault_tree.probability import Probability


class CCFGroup:
    """Represents a Common Cause Failure (CCF) group in a fault tree.

    A CCF group is a collection of basic events that have a common cause of failure.

    Attributes:
        name (str): The name of the CCF group.
        members (OrderedSet[BasicEvent]): A list of basic events that are members of the CCF group.
        prob (Optional[Probability]): The probability associated with the CCF group.
        model (Optional[str]): The CCF model used for the group.
        factors (OrderedSet[float]): The factors associated with the CCF model.
    """

    def __init__(self, name: str):
        """Initializes a CCFGroup with a unique name.

        Args:
            name (str): The identifier for the CCF group.
        """
        self.name: str = name
        self.members: OrderedSet[BasicEvent]
        self.prob: Optional[Probability] = None
        self.model: Optional[str] = None
        self.factors: OrderedSet[float]
