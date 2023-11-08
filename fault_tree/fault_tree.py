from collections import deque
from typing import Optional, Dict, Any, Deque
from ordered_set import OrderedSet

from fault_tree.event import BasicEvent, HouseEvent, Gate
from fault_tree import CCFGroup


class FaultTree:
    """Represents a fault tree for reliability and safety analysis.

    A fault tree is a graphical representation of the logical relationships between
    various subsystems and events within a system that can lead to a particular
    top-level failure event.

    Attributes:
        name (Optional[str]): The name of the fault tree or the system it represents.
        top_gate (Optional[Gate]): The top-level gate of the fault tree.
        top_gates (Optional[OrderedSet[Gate]]): A set of top-level gates if multiple exist.
        gates (OrderedSet[Gate]): A set of all gates within the fault tree.
        basic_events (OrderedSet[BasicEvent]): A set of all basic events within the fault tree.
        house_events (OrderedSet[HouseEvent]): A set of all house events within the fault tree.
        ccf_groups (OrderedSet[CCFGroup]): A set of all CCF groups within the fault tree.
        non_ccf_events (OrderedSet[BasicEvent]): A set of basic events not in any CCF group.
    """

    def __init__(self, name: Optional[str] = None):
        """Initializes an empty fault tree with an optional name.

        Args:
            name (Optional[str]): The name of the system described by the fault tree.
        """
        self.name: Optional[str] = name
        self.top_gate: Optional[Gate] = None
        self.top_gates: Optional[OrderedSet[Gate]] = None
        self.gates: OrderedSet[Gate] = OrderedSet()
        self.basic_events: OrderedSet[BasicEvent] = OrderedSet()
        self.house_events: OrderedSet[HouseEvent] = OrderedSet()
        self.ccf_groups: OrderedSet[CCFGroup] = OrderedSet()
        self.non_ccf_events: OrderedSet[BasicEvent] = OrderedSet()

    def add_gates(self, gates: OrderedSet[Gate], shallow: bool = False):
        """Adds a collection of gates to the fault tree.

        Args:
            gates (OrderedSet[Gate]): A set of gates to be added to the fault tree.
            shallow (bool): If True, only the specified gates are added without their descendants.
                            If False, all descendants of the specified gates are also added.
        """
        self.gates.update(gates)
        if not shallow:
            for gate in gates:
                self.basic_events.update(gate.b_arguments)
                self.house_events.update(gate.h_arguments)
                self.add_gates(gates=gate.g_arguments, shallow=False)

    def prune(self, gate: Optional[Gate]) -> bool:
        """Prunes a gate from the fault tree if it has only one argument.

        If no gate is provided, the top gate of the fault tree is pruned.

        This method is used to simplify the fault tree by removing gates that do not
        contribute to the logical structure of the tree.

        Args:
            gate (Optional[Gate]): The gate to be pruned. Defaults to the top gate of the fault tree.

        Returns:
            bool: True if the gate was pruned, False otherwise.
        """
        if gate is None:
            if self.top_gate is None:
                raise ValueError("No gate was provided, and the top gate is not set, so there is nothing to prune.")
            gate = self.top_gate
        if gate.num_arguments() == 1:
            if gate.num_parents() > 1:
                raise ValueError(f'Unexpected number of parents for gate {gate.name}')
            elif gate.num_parents() == 1:
                parent: Gate = gate.parents.pop()
                parent.g_arguments.discard(gate)
                for arg_type in [gate.g_arguments, gate.b_arguments, gate.h_arguments, gate.u_arguments]:
                    for arg in arg_type:
                        parent.add_argument(arg)
                self.gates.discard(gate)
                for child_gate in gate.g_arguments:
                    self.prune(child_gate)
                return True
        return False

    def __getstate__(self) -> Dict[str, Any]:
        """Retrieve the state of the FaultTree instance for pickling.

        Returns:
            Dict[str, Any]: The state of the instance as a dictionary.
        """
        return {
            'name': self.name,
            'top_gate': self.top_gate,
            'top_gates': self.top_gates,
            'gates': self.gates,
            'basic_events': self.basic_events,
            'house_events': self.house_events,
            'ccf_groups': self.ccf_groups,
            'non_ccf_events': self.non_ccf_events,
        }

    def __setstate__(self, state: Dict[str, Any]):
        """Sets the state of the FaultTree instance during unpickling.

        Args:
            state (Dict[str, Any]): The state of the instance as a dictionary.
        """
        self.name = state['name']
        self.top_gate = state['top_gate']
        self.top_gates = state['top_gates']
        self.gates = state['gates']
        self.basic_events = state['basic_events']
        self.house_events = state['house_events']
        self.ccf_groups = state['ccf_groups']
        self.non_ccf_events = state['non_ccf_events']

    def expr(self):
        """Returns the boolean expression string for the fault tree.

        The string is evaluated by recursively traversing the tree,
        starting from the top_gate.

        Returns:
            str: The boolean expression representing the fault tree.
        """
        if not self.top_gate:
            return ""

        return self.top_gate.expr()

    @staticmethod
    def toposort_gates(root_gates: OrderedSet[Gate], gates: OrderedSet[Gate]) -> Deque:
        """Sorts gates topologically starting from the root gate.

        The gate marks are used for the algorithm.
        After this sorting the marks are reset to None.

        Args:
            root_gates: The root gates of the graph.
            gates: Gates to be sorted.

        Returns:
            A deque of sorted gates.
        """

        for uninitialized_gate in gates:
            uninitialized_gate.mark = ""

        def visit(current_gate, final_list):
            """Recursively visits the given gate subtree to include into the list.

            Args:
                current_gate: The current gate.
                final_list: A deque of sorted gates.
            """
            assert current_gate.mark != "temp"
            if not current_gate.mark:
                current_gate.mark = "temp"
                for arg in current_gate.g_arguments:
                    visit(arg, final_list)
                current_gate.mark = "perm"
                final_list.appendleft(current_gate)

        sorted_gates = deque()

        for root_gate in root_gates:
            visit(root_gate, sorted_gates)

        assert len(sorted_gates) == len(gates)

        for gate in gates:
            gate.mark = None

        return sorted_gates
