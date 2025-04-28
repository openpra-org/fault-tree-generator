from collections import deque
from ordered_set import OrderedSet

from generator.event.basic_event import BasicEvent
from generator.event.Event import Event
from generator.event.house_event import HouseEvent


class Gate(Event):  # pylint: disable=too-many-instance-attributes
    """Representation of a fault tree gate.

    Attributes:
        operator: Logical operator of this formula.
        k_num: Min number for the combination operator.
        g_arguments: arguments that are gates.
        b_arguments: arguments that are basic events.
        h_arguments: arguments that are house events.
        u_arguments: arguments that are undefined.
        mark: Marking for various algorithms like toposort.
    """

    def __init__(self, name: str, operator, k_num=None):
        """Initializes a gate.

        Args:
            name: Identifier of the node.
            operator: Boolean operator of this formula.
            k_num: Min number for the combination operator.
        """
        super(Gate, self).__init__(name)
        self.mark = None
        self.operator = operator
        self.k_num = k_num
        self.g_arguments: OrderedSet[Gate] = OrderedSet()
        self.b_arguments: OrderedSet[BasicEvent] = OrderedSet()
        self.h_arguments: OrderedSet[HouseEvent] = OrderedSet()
        self.u_arguments: OrderedSet[Event] = OrderedSet()

    def num_arguments(self):
        """Returns the number of arguments."""
        return sum(
            len(x) for x in (self.b_arguments, self.h_arguments,
                             self.g_arguments, self.u_arguments))

    def add_basic_events(self, basic_events: OrderedSet[BasicEvent]):
        for basic_event in basic_events:
            basic_event.parents.add(self)
        self.b_arguments.update(basic_events)

    def add_basic_event(self, basic_event: BasicEvent):
        basic_event.parents.add(self)
        self.b_arguments.add(basic_event)

    def add_house_event(self, house_event: HouseEvent):
        house_event.parents.add(self)
        self.h_arguments.add(house_event)

    def add_gates(self, gates: OrderedSet['Gate']):
        for gate in gates:
            gate.parents.add(self)
        self.g_arguments.update(gates)

    def add_gate(self, gate: 'Gate'):
        gate.parents.add(self)
        self.g_arguments.add(gate)

    def add_argument(self, argument):
        """Adds argument into a collection of gate arguments.

        Note that this function also updates the parent set of the argument.
        Duplicate arguments are ignored.
        The logic of the Boolean operator is not taken into account
        upon adding arguments to the gate.
        Therefore, no logic checking is performed
        for repeated or complement arguments.

        Args:
            argument: Gate, HouseEvent, BasicEvent, or Event argument.
        """
        argument.parents.add(self)
        if isinstance(argument, Gate):
            self.g_arguments.add(argument)
        elif isinstance(argument, BasicEvent):
            self.b_arguments.add(argument)
        elif isinstance(argument, HouseEvent):
            self.h_arguments.add(argument)
        else:
            assert isinstance(argument, Event)
            self.u_arguments.add(argument)

    def get_ancestors(self):
        """Collects ancestors from this gate.

        Returns:
            A set of ancestors.
        """
        ancestors = OrderedSet([self])
        parents = deque(self.parents)  # to avoid recursion
        while parents:
            parent = parents.popleft()
            if parent not in ancestors:
                ancestors.add(parent)
                parents.extend(parent.parents)
        return ancestors

    def to_xml(self, printer, nest=False):
        """Produces the Open-PSA MEF XML definition of the gate.

        Args:
            printer: The output stream.
            nest: Nesting of NOT connectives in formulas.
        """

        def arg_to_xml(type_str, arg):
            """Produces XML string representation of an argument."""
            return "<%s name=\"%s\"/>\n" % (type_str, arg.name)

        def args_to_xml(type_str, args):
            """Produces XML string representation of arguments."""
            return "".join(arg_to_xml(type_str, arg) for arg in args)

        def convert_formula(gate, nest=False):
            """Converts the formula of a gate into XML representation."""
            mef_xml = ""
            if gate.operator != "null":
                mef_xml += "<" + gate.operator
                if gate.operator == "atleast":
                    mef_xml += " min=\"" + str(gate.k_num) + "\""
                mef_xml += ">\n"
            mef_xml += args_to_xml("house-event", gate.h_arguments)
            mef_xml += args_to_xml("basic-event", gate.b_arguments)
            mef_xml += args_to_xml("event", gate.u_arguments)

            def converter(arg_gate):
                """Converter for single nesting NOT connective."""
                if gate.operator != "not" and arg_gate.operator == "not":
                    return convert_formula(arg_gate)
                return arg_to_xml("gate", arg_gate)

            if nest:
                mef_xml += "".join(converter(x) for x in gate.g_arguments)
            else:
                mef_xml += args_to_xml("gate", gate.g_arguments)

            if gate.operator != "null":
                mef_xml += "</" + gate.operator + ">"
            return mef_xml

        printer('<define-gate name="', self.name, '">')
        printer(convert_formula(self, nest))
        printer('</define-gate>')

    def to_aralia(self, printer):
        """Produces the Aralia definition of the gate.

        The transformation to the Aralia format
        does not support complement or undefined arguments.

        Args:
            printer: The output stream.

        Raises:
            KeyError: The gate operator is not supported.
        """
        assert not self.u_arguments

        def get_format(operator):
            """Determins formatting for the gate operator."""
            if operator == "atleast":
                return "@(" + str(self.k_num) + ", [", ", ", "])"
            return {
                "and": ("(", " & ", ")"),
                "or": ("(", " | ", ")"),
                "xor": ("(", " ^ ", ")"),
                "not": ("~(", "", ")")
            }[operator]

        line = [self.name, " := "]
        line_start, div, line_end = get_format(self.operator)
        line.append(line_start)
        args = []
        for h_arg in self.h_arguments:
            args.append(h_arg.name)

        for b_arg in self.b_arguments:
            args.append(b_arg.name)

        for g_arg in self.g_arguments:
            args.append(g_arg.name)
        line.append(div.join(args))
        line.append(line_end)
        printer("".join(line))
