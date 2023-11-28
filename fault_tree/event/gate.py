from collections import deque
from ordered_set import OrderedSet
from typing import Optional, Union, TYPE_CHECKING, Set
from pyeda.inter import bddvars, expr2bdd, expr

from .event import Event
from .basic_event import BasicEvent
from .house_event import HouseEvent

if TYPE_CHECKING:
    from fault_tree.event import Gate as GateType
else:
    GateType = 'Gate'

# Assuming OperatorType is a custom type that you have defined elsewhere in your code.
# If it's a string or another type, adjust the type hint accordingly.
OperatorType = str  # Replace with the actual type if it's not a string


class Gate(Event):
    """Representation of a fault tree gate.

    A gate in a fault tree represents a logical operator that combines the states of
    its child events to determine its own state.

    Attributes:
        name (str): Identifier of the gate.
        operator (OperatorType): Logical operator of this gate.
        k_num (Optional[int]): Minimum number for the combination operator (used in k-out-of-n gates).
        g_arguments (OrderedSet[Gate]): Child gates that are arguments of this gate.
        b_arguments (OrderedSet[BasicEvent]): Basic events that are arguments of this gate.
        h_arguments (OrderedSet[HouseEvent]): House events that are arguments of this gate.
        u_arguments (OrderedSet[Event]): Undefined events that are arguments of this gate.
        mark (Optional[str]): Marking for various algorithms like topological sort.
    """

    def __init__(self, name: str, operator: OperatorType, k_num: Optional[int] = None):
        """Initializes a gate with a name, operator, and an optional k_num.

        Args:
            name (str): Identifier of the gate.
            operator (OperatorType): Logical operator of this gate.
            k_num (Optional[int]): Minimum number for the combination operator (used in k-out-of-n gates).
        """
        super().__init__(name)
        self.mark: Optional[str] = None
        self.operator: OperatorType = operator
        self.k_num: Optional[int] = k_num
        self.g_arguments: OrderedSet[Gate] = OrderedSet()
        self.b_arguments: OrderedSet[BasicEvent] = OrderedSet()
        self.h_arguments: OrderedSet[HouseEvent] = OrderedSet()
        self.u_arguments: OrderedSet[Event] = OrderedSet()

    def num_arguments(self) -> int:
        """Returns the total number of arguments (children) of the gate.

        Returns:
            int: The total number of child events (gates, basic events, house events, and undefined events).
        """
        return len(self.g_arguments) + len(self.b_arguments) + len(self.h_arguments) + len(self.u_arguments)

    def add_basic_events(self, basic_events: OrderedSet[BasicEvent]):
        """Adds multiple basic events as children of the gate.

        Args:
            basic_events (OrderedSet[BasicEvent]): A set of basic events to be added as children.
        """
        for basic_event in basic_events:
            self.add_basic_event(basic_event)

    def add_basic_event(self, basic_event: BasicEvent):
        """Adds a single basic event as a child of the gate.

        Args:
            basic_event (BasicEvent): The basic event to be added as a child.
        """
        if basic_event in self.b_arguments:
            raise AssertionError("The basic event is already a child of this gate.")
        self.b_arguments.add(basic_event)
        basic_event.parents.add(self)

    def add_house_events(self, house_events: OrderedSet[HouseEvent]):
        """Adds multiple house events as children of the gate.

        Args:
            house_events (OrderedSet[HouseEvent]): A set of house events to be added as children.
        """
        for house_event in house_events:
            self.add_house_event(house_event)

    def add_house_event(self, house_event: HouseEvent):
        """Adds a house event as a child of the gate.

        Args:
            house_event (HouseEvent): The house event to be added as a child.
        """
        if house_event in self.h_arguments:
            raise AssertionError("The house event is already a child of this gate.")
        self.h_arguments.add(house_event)
        house_event.parents.add(self)

    def add_events(self, events: OrderedSet[Event]):
        """Adds multiple events of unknown type as children of the gate.

        Args:
            events (OrderedSet[Event]): A set of events of unknown type to be added as children.
        """
        for event in events:
            self.add_event(event)

    def add_event(self, event: Event):
        """Adds an event of unknown type as a child of the gate.

        Args:
            event (Event): The house event to be added as a child.
        """
        if event in self.u_arguments:
            raise AssertionError("The event is already a child of this gate.")
        self.u_arguments.add(event)
        event.parents.add(self)

    def add_gates(self, gates: OrderedSet[GateType]):
        """Adds multiple gates as children of this gate.

        Args:
            gates (OrderedSet[Gate]): A set of gates to be added as children.
        """
        for gate in gates:
            self.add_gate(gate)

    def add_gate(self, gate: GateType):
        """Adds a single gate as a child of this gate.

        Args:
            gate (Gate): The gate to be added as a child.
        """
        if gate in self.g_arguments:
            raise AssertionError("The gate is already a child of this gate.")
        self.g_arguments.add(gate)
        gate.parents.add(self)

    def add_arguments(self, arguments: OrderedSet[Union[GateType, BasicEvent, HouseEvent, Event]]):
        """Adds multiple arguments (child events) to the gate.

        This method updates the parent set of each argument and adds it to the appropriate
        collection of arguments based on its type. Duplicate arguments are ignored.

        Args:
            arguments (OrderedSet[Union[Gate, BasicEvent, HouseEvent, Event]]): The events to be added as children.
        """
        for argument in arguments:
            self.add_argument(argument)

    def add_argument(self, argument: Union[GateType, BasicEvent, HouseEvent, Event]):
        """Adds an argument (child event) to the gate.

        This method updates the parent set of the argument and adds it to the appropriate
        collection of arguments based on its type. Duplicate arguments are ignored.

        Args:
            argument (Union[Gate, BasicEvent, HouseEvent, Event]): The event to be added as a child.
        """
        argument.parents.add(self)
        if isinstance(argument, Gate):
            self.add_gate(argument)
        elif isinstance(argument, BasicEvent):
            self.add_basic_event(argument)
        elif isinstance(argument, HouseEvent):
            self.add_house_event(argument)
        else:
            assert isinstance(argument, Event), "Argument must be an instance of Event or its subclasses."
            self.add_event(argument)

    def get_ancestors(self) -> OrderedSet[Event]:
        """Collects and returns a set of all ancestor events of this gate.

        This method performs a breadth-first search to find all ancestors without recursion.

        Returns:
            OrderedSet[Event]: A set of all ancestor events.
        """
        ancestors: OrderedSet[Event] = OrderedSet([self])
        parents = deque(self.parents)
        while parents:
            parent = parents.popleft()
            if parent not in ancestors:
                ancestors.add(parent)
                parents.extend(parent.parents)
        return ancestors

    def expr(self):
        """Returns the symbolic boolean expression string for the gate.

        The string is built using symbols for logical operations:
        '|' for OR, '&' for AND, '~' for NOT, '^' for XOR.

        Returns:
            str: The symbolic boolean expression representing the gate.
        """
        # Helper function to format the arguments of the gate
        def format_arguments(arguments):
            return [arg.expr() for arg in arguments]

        # Format the arguments for basic events, house events, and child gates
        b_args = format_arguments(self.b_arguments)
        h_args = format_arguments(self.h_arguments)
        u_args = format_arguments(self.u_arguments)
        g_args = format_arguments(self.g_arguments)

        # Combine all arguments into a single list
        all_args = b_args + h_args + u_args + g_args

        if not all_args:
            return f"{self.name}"

        # Build the expression based on the gate operator
        if self.operator == "and":
            return '(' + ' & '.join(all_args) + ')'
        elif self.operator == "or":
            return '(' + ' | '.join(all_args) + ')'
        elif self.operator == "not":
            # NOT gates should only have one argument
            assert len(all_args) == 1, "NOT gate should have exactly one argument"
            return '~' + all_args[0]
        elif self.operator == "xor":
            # XOR is represented as a ^ b
            # For more than two arguments, XOR is associative: a ^ b ^ c
            return '(' + ' ^ '.join(all_args) + ')'
        elif self.operator == "atleast":
            # For k-out-of-n gates, we will use a special notation: atleast_k(args)
            # This is not a standard operator in pyeda, so you may need to handle it separately
            return f"atleast_{self.k_num}(" + ', '.join(all_args) + ')'
        else:
            raise ValueError(f"Unknown gate operator: {self.operator}")

    def to_bdd(self, var_order: Optional[OrderedSet[str]] = None):
        """Converts the gate to a BDD based on its logical operation and child events.

        Args:
            var_order (Optional[List[str]]): The order of variables for the BDD.

        Returns:
            BDD: The BDD representation of the gate.
        """
        if self.operator == "and":
            return expr2bdd(expr('&', *[arg.to_bdd() for arg in self.g_arguments]))
        elif self.operator == "or":
            return expr2bdd(expr('|', *[arg.to_bdd() for arg in self.g_arguments]))
        elif self.operator == "not":
            assert len(self.g_arguments) == 1, "NOT gate should have exactly one argument"
            return ~next(iter(self.g_arguments)).to_bdd()
        # Add more cases for other gate types if necessary
        else:
            raise ValueError(f"Unknown gate operator: {self.operator}")

    def to_openfta(self):

        def format_arguments(arguments):
            return [arg.to_openfta() for arg in arguments]

        # Format the arguments for basic events, house events, and child gates
        b_args = format_arguments(self.b_arguments)
        h_args = format_arguments(self.h_arguments)
        # u_args = format_arguments(self.u_arguments)
        # g_args = format_arguments(self.g_arguments)

        # Combine all arguments into a single list
        all_args = b_args + h_args #+ u_args + g_args

        symbol = 'O' if self.operator == 'or' else 'A'
        num_args = len(all_args)
        label = f"{symbol} {self.name} {num_args}"
        all_args.insert(0, label)

        return all_args

