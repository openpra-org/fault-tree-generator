from fault_tree.event import Event
from typing import Literal, Optional
from ordered_set import OrderedSet
from pyeda.inter import expr2bdd, exprvar


class HouseEvent(Event):
    """Representation of a house event in a fault tree.

    A house event is a special type of event that has a fixed state and does not depend on other events.

    Attributes:
        name (str): A specific name that identifies this house event.
        state (Literal['true', 'false', True, False]): The state of the house event, which can be either "true" or
        "false".
    """

    VALID_STATES = {'true', 'false', True, False}

    def __init__(self, name: str, state: Optional[Literal['true', 'false', True, False]]):
        """Initializes a HouseEvent with a unique name and a fixed state.

        Args:
            name (str): Identifier for the house event.
            state (Literal['true', 'false', True, False]): Boolean state string of the constant, either "true" or "false".
        """
        if state and state not in self.VALID_STATES:
            raise ValueError(f"Invalid state: {state}. Valid states are: {self.VALID_STATES}")
        super().__init__(name)
        if state is None:
            self.state: Literal['true', 'false'] = "false"
        else:
            self.state: Literal['true', 'false'] = state

    @property
    def state(self) -> Literal['true', 'false']:
        return self._state

    @state.setter
    def state(self, value: Literal['true', 'false']):
        if value not in self.VALID_STATES:
            raise ValueError(f"Invalid state: {value}. Valid states are: {self.VALID_STATES}")
        self._state = value

    def to_bdd(self, var_order: Optional[OrderedSet[str]] = None):
        """Converts the house event to a BDD constant based on its state.

        Args:
            var_order (Optional[OrderedSet[str]]): The order of variables for the BDD.

        Returns:
            BDD: The BDD constant representing the house event.
        """
        # Create a BDD variable for the house event
        bdd_var = exprvar(self.name)

        # Convert the BDD variable to its constant value based on the state of the house event
        if self.state in ['true', True]:
            return expr2bdd(bdd_var)
        else:
            return expr2bdd(~bdd_var)
