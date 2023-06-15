# Copyright (C) 2014-2018 Olzhas Rakhimov
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Fault tree classes and common facilities."""

from collections import deque
from math import comb
import json
from fractions import Fraction
from decimal import Decimal
class Event:
    """Representation of a base class for an event in a fault tree.

    Attributes:
        name: A specific name that identifies this node.
        parents: A set of parents of this node.
    """

    def __init__(self, name):
        """Constructs a new node with a unique name.

        Note that the tracking of parents introduces a cyclic reference.

        Args:
            name: Identifier for the node.
        """
        self.name = name
        self.parents = set()

    def is_common(self):
        """Indicates if this node appears in several places."""
        return len(self.parents) > 1

    def is_orphan(self):
        """Determines if the node has no parents."""
        return not self.parents

    def num_parents(self):
        """Returns the number of unique parents."""
        return len(self.parents)

    def add_parent(self, gate):
        """Adds a gate as a parent of the node.

        Args:
            gate: The gate where this node appears.
        """
        assert gate not in self.parents
        self.parents.add(gate)


class BasicEvent(Event):
    """Representation of a basic event in a fault tree.

    Attributes:
        prob: Probability of failure of this basic event.
    """

    def __init__(self, name, prob, num_basic):
        """Initializes a basic event node.

        Args:
            name: Identifier of the node.
            prob: Probability of the basic event.
        """

        super(BasicEvent,self).__init__(name)
        self.prob = prob
        self.num_basic = num_basic

    def to_xml(self, printer):
        """Produces the Open-PSA MEF XML definition of the basic event."""
        printer('<define-basic-event name="', self.name, '">')
        printer('<float value="', self.prob, '"/>')
        printer('</define-basic-event>')

    def to_aralia(self, printer):
        """Produces the Aralia definition of the basic event."""
        printer('p(', self.name, ') = ', self.prob)


    def to_SAPHIRE_json_printer(self, printer):

        """Produces SaphSolver JSON definition of the basic event"""
        printer('{')
        printer('"id": "', self.name.strip('B'), '",')
        printer('"corrgate": "0",')
        printer('"name": "', self.name, '",')
        printer('"evworkspacepair": {')
        printer('"ph": 1,')
        printer('"mt": 1')
        printer('},')
        printer('"value": ', self.prob, ',')
        printer('"initf": "",')
        printer('"processf": "",')
        printer('"calctype": "1"')
        if int(self.name.strip('B')) == self.num_basic:
              printer('}')
        else:
              printer('},')


    def to_SAPHIRE_json_object(self, base):

        """Produces SaphSolver JSON definition of the basic event using json-python library"""

        eventList = base['saphiresolveinput']['eventlist']
        eventList[4]['id'] = int(self.name.strip('B'))
        eventList[4]['corrgate'] = 0
        eventList[4]['name'] = self.name
        eventList[4]['evworkspacepair']['ph'] = 1
        eventList[4]['evworkspacepair']['mt'] = 1
        eventList[4]['value'] = self.prob
        eventList[4]['initf'] = " "
        eventList[4]['processf'] = " "
        eventList[4]['calctype'] = "1"
        dictCopy = eventList[4].copy()
        eventList.append(dictCopy)


    def to_OpenPRA_json_printer(self, printer):
        """Produces OpenPRA JSON definition of the basic event."""
        printer('"', self.name, '": {')
        printer('"role": "public",')
        printer('"label": {')
        printer('"name": "Basic Event:', self.name, '",')
        printer('"description": ""')
        printer('},')
        printer('"expression": {')
        printer('"value": ', self.prob, ',')
        printer('"_proxy": "Float"')
        printer('},')
        printer('"source_type": "hcl"')
        if int(self.name.strip('B')) == self.num_basic:
              printer('}')
        else:
              printer('},')


    def to_SAPHIRE_json_object(self, base):

        """Produces SaphSolver JSON definition of the basic event using json-python library"""

        eventList = base['saphiresolveinput']['eventlist']
        eventList[4]['id'] = int(self.name.strip('B'))
        eventList[4]['corrgate'] = 0
        eventList[4]['name'] = self.name
        eventList[4]['evworkspacepair']['ph'] = 1
        eventList[4]['evworkspacepair']['mt'] = 1
        eventList[4]['value'] = self.prob
        eventList[4]['initf'] = " "
        eventList[4]['processf'] = " "
        eventList[4]['calctype'] = "1"
        dictCopy = eventList[4].copy()
        eventList.append(dictCopy)


    def to_OpenPRA_json_printer(self, printer):
        """Produces OpenPRA JSON definition of the basic event."""
        printer('"', self.name, '": {')
        printer('"role": "public",')
        printer('"label": {')
        printer('"name": "Basic Event:', self.name, '",')
        printer('"description": ""')
        printer('},')
        printer('"expression": {')
        printer('"value": ', self.prob, ',')
        printer('"_proxy": "Float"')
        printer('},')
        printer('"source_type": "hcl"')
        if int(self.name.strip('B')) == self.num_basic:
              printer('}')
        else:
              printer('},')


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
        printer('<constant value="', self.state, '"/>')
        printer('</define-house-event>')

    def to_aralia(self, printer):
        """Produces the Aralia definition of the house event."""
        printer('s(', self.name, ') = ', self.state)


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

    def __init__(self, name, operator, k_num=None):
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
        self.g_arguments = set()
        self.b_arguments = set()
        self.h_arguments = set()
        self.u_arguments = set()
        # self.members = ["B40", "B10"]

    def num_arguments(self):
        """Returns the number of arguments."""

        return sum(
            len(x) for x in (self.b_arguments, self.h_arguments,
                             self.g_arguments, self.u_arguments))

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
        ancestors = set([self])
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
            # print("self.members", self.members)
            # if gate.b_arguments:
            #     print("BE", gate.b_arguments)
            #     # OpenPRA_JSON_format += "\"eventinput\": [\n"
            #     for i in gate.b_arguments:
            #         if i in self.members:
            # # for member in self.members:
            # #     if gate.b_arguments == "B59":
            #             mef_xml += args_to_xml("basic-event", "CCF")

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

    def to_SAPHIRE_JSON_printer(self, printer, last=True):
        """Produces the JSON definition of the gate.

        Args:
            printer: The output stream.
            nest: Nesting of NOT connectives in formulas.
        """

        def arg_to_JSON(type_str, arg):
            """Produces JSON string representation of an argument."""
            return "%s\":%s,\n" % (type_str, arg.name)
        def args_to_JSON(type_str,args):
            """Produces JSON string representation of arguments."""
            return "".join(arg_to_JSON(type_str, arg) for arg in args)

        def gate_name_to_number(arg):
            return "%s,\n" % (arg.name.strip('G'))
        def gate_name_to_number_last(arg):
            return "%s\n" % (arg.name.strip('G'))

        def basic_name_to_number(arg):
            return "%s,\n" % (arg.name.strip('B'))
        def basic_name_to_number_last(arg):
            return "%s\n" % (arg.name.strip('B'))


        def convert_formula(gate, last=False):
            """Converts the formula of a gate into SAPHIRE JSON representation."""
            JSON_format = ""
            if gate.operator != "null":
                JSON_format += "\"gatetype\":\"" + gate.operator
                if gate.operator == "atleast":
                    JSON_format += " min=\"" + str(gate.k_num) + "\""
                JSON_format += "\",\n"
            num_g = int(str(len(gate.g_arguments)))
            num_b = int(str(len(gate.b_arguments)))
            total_num = num_g + num_b

            JSON_format += '"numinputs":"' + str(total_num) + "\",\n"
            if gate.g_arguments:
                JSON_format += "\"gateinput\": [\n"
                for i in gate.g_arguments:
                    num = list(gate.g_arguments)
                    if i == num[-1]:
                        JSON_format += gate_name_to_number_last(i)
                    else:
                        JSON_format += gate_name_to_number( i)
                if gate.b_arguments:
                    JSON_format += "],\n"
                else:
                    JSON_format += "]"

            if gate.b_arguments:
                JSON_format += "\"eventinput\": [\n"
                for i in gate.b_arguments:
                    num = list(gate.b_arguments)
                    if i == num[-1]:
                        JSON_format += basic_name_to_number_last(i)
                    else:
                        JSON_format += basic_name_to_number( i)
                JSON_format += "]"
            return JSON_format


        printer('{')
        printer('\"gateid\":', self.name.strip('Groot'), ",")
        printer(convert_formula(self, last))


    def to_SAPHIRE_JSON_object(self, base, last=True):
        """Produces the SAPHSOLVE JSON object definition of the gate.

        Args:
            printer: The output stream.
            nest: Nesting of NOT connectives in formulas.
        """

        def arg_to_JSON(type_str, arg):
            """Produces JSON string representation of an argument."""
            return "%s\":%s,\n" % (type_str, arg.name)
        def args_to_JSON(type_str,args):
            """Produces JSON string representation of arguments."""
            return "".join(arg_to_JSON(type_str, arg) for arg in args)

        def gate_name_to_number(arg):
            return arg.name.strip('\"G')
        def basic_name_to_number(arg):
            return arg.name.strip('\"B')


        def convert_formula(gate,arg, last=False):
            """Converts the formula of a gate into SAPHIRE JSON representation."""
            gateList = base['saphiresolveinput']['faulttreelist'][0]['gatelist']


            num_g = len(gate.g_arguments)
            num_b = len(gate.b_arguments)
            total_num = num_g + num_b
            print(total_num)
            # JSON_format = ""
            if gate.operator != "null":
                gateList[1]['gatetype'] = gate.operator
                if gate.operator == "atleast":
                    fraction_value = f"{gate.k_num}/{total_num}"
                    gateList[1]['gatetype'] = fraction_value

            gateList[1]['numinputs'] = total_num
            gate_list = list()
            if gate.g_arguments:

                for i in gate.g_arguments:
                    gate_list.append(int(gate_name_to_number(i)))
                    gateList[1]['gateinput'] = gate_list

            else:
                    gateList[1]['gateinput'] = 0
                    del gateList[1]['gateinput']

            event_list = list()
            if gate.b_arguments:

                for i in gate.b_arguments:
                    event_list.append(int(basic_name_to_number(i)))
                    gateList[1]['eventinput']= event_list

            else:
                gateList[1]['eventinput'] = 0
                del gateList[1]['eventinput']
            return gateList


        gateList = base['saphiresolveinput']['faulttreelist'][0]['gatelist']

        gateList[1]['gateid'] = int(self.name.strip('Groot'))
        convert_formula(self, last)

        dictCopy = gateList[1].copy()
        gateList.append(dictCopy)


    def to_OpenPRA_JSON_printer(self, printer, last=True):
        """Produces the OpenPRA JSON definition of the gate.

        Args:
            printer: The output stream.
            nest: Nesting of NOT connectives in formulas.
        """

        def arg_to_JSON(type_str, arg):
            """Produces JSON string representation of an argument."""
            return "%s\":%s,\n" % (type_str, arg.name)
        def args_to_JSON(type_str,args):
            """Produces JSON string representation of arguments."""
            return "".join(arg_to_JSON(type_str, arg) for arg in args)

        def gate_name_to_number(arg):
            return "%s" % (arg.name)
        def gate_name_to_number_last(arg):
            return "%s" % (arg.name)

        def basic_name_to_number(arg):
            return "%s" % (arg.name)
        def basic_name_to_number_last(arg):
            return "%s" % (arg.name)


        def convert_formula(gate, last=False):
            """Converts the formula of a gate into SAPHIRE JSON representation."""
            # capital_gate = upper(gate.opertaor)
            OpenPRA_JSON_format = ""
            if gate.operator != "null":
                OpenPRA_JSON_format += "\"name\":\"" + str.upper(gate.operator) + " Gate:" + self.name.strip('root') + "\",\n" + '"description":""\n },'
                if gate.operator == "k/n":
                    OpenPRA_JSON_format += " min=\"" + str(gate.k_num) + "\""
                OpenPRA_JSON_format += "\n"
            num_g = int(str(len(gate.g_arguments)))
            num_b = int(str(len(gate.b_arguments)))
            num_g + num_b

            OpenPRA_JSON_format += '"formula": {\n'
            OpenPRA_JSON_format += '"formulas": [\n'
            # OpenPRA_JSON_format += '{\n'

            if gate.g_arguments:
                # OpenPRA_JSON_format += "\"gateinput\": [\n"
                for i in gate.g_arguments:
                    num = list(gate.g_arguments)
                    if i == num[-1]:
                        OpenPRA_JSON_format += "{\n"
                        OpenPRA_JSON_format += "\"name\":" + "\"" + gate_name_to_number_last(i) + "\",\n"
                        OpenPRA_JSON_format += '"reference_type": "gates",\n'
                        OpenPRA_JSON_format += '"tree_id": null,\n'
                        OpenPRA_JSON_format += '"path": "",\n'
                        OpenPRA_JSON_format += '"_proxy": "EventReference"\n'
                        if gate.b_arguments:
                            OpenPRA_JSON_format += "},\n"
                        else:
                            OpenPRA_JSON_format += "}\n"
                    else:
                        OpenPRA_JSON_format += "{\n"
                        OpenPRA_JSON_format += "\"name\":" + "\"" + gate_name_to_number(i) + "\",\n"
                        OpenPRA_JSON_format += '"reference_type": "gates",\n'
                        OpenPRA_JSON_format += '"tree_id": null,\n'
                        OpenPRA_JSON_format += '"path": "",\n'
                        OpenPRA_JSON_format += '"_proxy": "EventReference"\n'
                        OpenPRA_JSON_format += "},\n"
                if not gate.b_arguments:
                    OpenPRA_JSON_format += "],"
                # else:
                #     OpenPRA_JSON_format += "],"

            if gate.b_arguments:
                # OpenPRA_JSON_format += "\"eventinput\": [\n"
                for i in gate.b_arguments:
                    num = list(gate.b_arguments)
                    if i == num[-1]:
                        OpenPRA_JSON_format += "{\n"
                        OpenPRA_JSON_format += "\"name\":" + "\"" + basic_name_to_number_last(i) + "\",\n"
                        OpenPRA_JSON_format += '"reference_type": "basic_events",\n'
                        OpenPRA_JSON_format += '"tree_id": null,\n'
                        OpenPRA_JSON_format += '"path": "",\n'
                        OpenPRA_JSON_format += '"_proxy": "EventReference"\n'
                        OpenPRA_JSON_format += "}\n"
                    else:
                        OpenPRA_JSON_format += "{\n"
                        OpenPRA_JSON_format += "\"name\":" + "\"" + basic_name_to_number(i) + "\",\n"
                        OpenPRA_JSON_format += '"reference_type": "basic_events",\n'
                        OpenPRA_JSON_format += '"tree_id": null,\n'
                        OpenPRA_JSON_format += '"path": "",\n'
                        OpenPRA_JSON_format += '"_proxy": "EventReference"\n'
                        OpenPRA_JSON_format += "},\n"
                OpenPRA_JSON_format += "],"

            OpenPRA_JSON_format += "\n\"expr\"" + ':"' + gate.operator + '",\n'
            OpenPRA_JSON_format += '"_proxy": "LogicalExpression"\n'
            # OpenPRA_JSON_format += "}," # to close every gate

            return OpenPRA_JSON_format
        printer('"',self.name.strip('root'),'":', "{")
        printer('"role": "public",')
        printer('"label": {')
        printer(convert_formula(self, last))



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


class CcfGroup:  # pylint: disable=too-few-public-methods
    """Representation of CCF groups in a fault tree.

    Attributes:
        name: The name of an instance CCF group.
        members: A collection of members in a CCF group.
        prob: Probability for a CCF group.
        model: The CCF model chosen for a group.
        factors: The factors of the CCF model.
    """

    def __init__(self, name):
        """Constructs a unique CCF group with a unique name.

        Args:
            name: Identifier for the group.
        """
        self.name = name
        self.members = []
        self.prob = None
        self.model = None
        self.factors = []

    def to_xml(self, printer):
        """Produces the Open-PSA MEF XML definition of the CCF group."""
        printer('<define-CCF-group name="', self.name, '"', ' model="',
                self.model, '">')
        printer('<members>')
        for member in self.members:
            printer('<basic-event name="', member.name, '"/>')
        printer('</members>')

        printer('<distribution>')
        printer('<float value="', self.prob, '"/>')
        printer('</distribution>')

        printer('<factors>')
        # assert self.model == "MGL"
        assert self.factors

        if self.model == "MGL":
            level = 2
        else:
            level = 1
        for factor in self.factors:
            printer('<factor level="', level, '">')
            printer('<float value="', factor, '"/>')
            printer('</factor>')
            level += 1
        printer('</factors>')

        printer('</define-CCF-group>')

    def to_SAPHIRE_json_object(self, base):

        """Produces SaphSolver JSON definition of common cause failures (alpha-factor model) using json-python library"""
        for member in self.members:
            if self.model == "alpha-factor":
                eventList = base['saphiresolveinput']['eventlist']
                eventList[4]['id'] = int(member.name.strip('B'))
                eventList[4]['corrgate'] = 0
                eventList[4]['name'] = member.name + "_cc"
                eventList[4]['evworkspacepair']['ph'] = 1
                eventList[4]['evworkspacepair']['mt'] = 1
                eventList[4]['value'] = self.prob
                eventList[4]['initf'] = " "
                eventList[4]['processf'] = " "
                eventList[4]['calctype'] = "1"
                dictCopy = eventList[4].copy()
                eventList.append(dictCopy)

    def to_SAPHIRE_json_ccf_BE(self):
     # """this function calculate the ccf basic event probability value for SAPHIRE json """
        assert self.factors
        Q_total = self.prob
        m = len(self.factors)
        k = range(m)
        print(m,k)
        # level = 1
        ccf_values = []
        # print (len(self.factors))
        for factor in self.factors:
            Q= self.prob

            ccf_values.append(Q)
        return ccf_values

    def returned_ccf_list(self):

        returned_ccf_values = CcfGroup.to_SAPHIRE_json_ccf_BE(self)

        return returned_ccf_values


    def to_SAPHIRE_json_ccf(self,base):
        if not hasattr(self, "values"):
            self.values = CcfGroup.to_SAPHIRE_json_ccf_BE(self)
        # counter = 0
        eventList = base['saphiresolveinput']['eventlist']
        eventList[4]['id'] = int(self.name.strip("CCF") + "001")
        eventList[4]['corrgate'] = 0
        eventList[4]['name'] = self.name
        eventList[4]['evworkspacepair']['ph'] = 1
        eventList[4]['evworkspacepair']['mt'] = 1
        eventList[4]['value'] = self.values.pop(0)
        eventList[4]['initf'] = " "
        eventList[4]['processf'] = " "
        eventList[4]['calctype'] = "R"
        dictCopy = eventList[4].copy()
        eventList.append(dictCopy)
        # counter +=1

        # print("counter", counter)


class FaultTree:  # pylint: disable=too-many-instance-attributes
    """Representation of a fault tree for general purposes.

    Attributes:
        name: The name of a fault tree.
        top_gate: The root gate of the fault tree.
        top_gates: Container of top gates. Single one is the default.
        gates: A set of all gates that are created for the fault tree.
        basic_events: A list of all basic events created for the fault tree.
        house_events: A list of all house events created for the fault tree.
        ccf_groups: A collection of created CCF groups.
        non_ccf_events: A list of basic events that are not in CCF groups.
    """

    def __init__(self, name=None):
        """Initializes an empty fault tree.

        Args:
            name: The name of the system described by the fault tree container.
        """

        self.name = name
        self.top_gate = None
        self.top_gates = None
        self.gates = []
        self.basic_events = []
        self.house_events = []
        self.ccf_groups = []
        self.non_ccf_events = []  # must be assigned directly.
        # self.factors = []

    def to_xml(self, printer, nest=False):
        """Produces the Open-PSA MEF XML definition of the fault tree.

        The fault tree is produced breadth-first.
        The output XML representation is not formatted for human readability.
        The fault tree must be valid and well-formed.

        Args:
            printer: The output stream.
            nest: A nesting factor for the Boolean formulae.
        """
        printer('<opsa-mef>')
        printer('<define-fault-tree name="', self.name, '">')

        sorted_gates = toposort_gates(self.top_gates or [self.top_gate],
                                      self.gates)
        for gate in sorted_gates:
            gate.to_xml(printer, nest)

        for ccf_group in self.ccf_groups:
            ccf_group.to_xml(printer)
        printer('</define-fault-tree>')

        printer('<model-data>')

        for basic_event in (self.non_ccf_events
                            if self.ccf_groups else self.basic_events):
            basic_event.to_xml(printer)



        for house_event in self.house_events:
            house_event.to_xml(printer)
        printer('</model-data>')
        printer('</opsa-mef>')

    def to_aralia(self, printer):
        """Produces the Aralia definition of the fault tree.

        Note that the Aralia format does not support advanced features.
        The fault tree must be valid and well formed for printing.

        Args:
            printer: The output stream.

        Raises:
            KeyError: Some gate operator is not supported.
        """
        printer(self.name)
        printer()

        sorted_gates = toposort_gates([self.top_gate], self.gates)
        for gate in sorted_gates:
            gate.to_aralia(printer)

        printer()

        for basic_event in self.basic_events:
            basic_event.to_aralia(printer)

        printer()

        for house_event in self.house_events:
            house_event.to_aralia(printer)

    def to_SAPHIRE_json_printer(self, printer, nest=False):
        """Produces SAPHIRE JSON definition of the fault tree.

        The fault tree is produced breadth-first.
        The output SAPHIRE JSON representation is not formatted for human readability.
        The fault tree must be valid and well-formed.

        Args:
            printer: The output stream.
            nest: A nesting factor for the Boolean formulae.
        """

        sorted_gates = toposort_gates(self.top_gates or [self.top_gate],
                                      self.gates)
        for gate in sorted_gates:
            gate.to_SAPHIRE_JSON_printer(printer, nest)
            if gate == sorted_gates[-1]:
                printer("}")
            else:
                printer("},")

        printer(']')
        printer('}')
        printer('],')
        printer('"eventlist": [')
        printer('{')
        printer('"id":', '"99999"', ',')
        printer('"corrgate": "0",')
        printer('"name": "', '<TRUE>', '",')
        printer('"evworkspacepair": {')
        printer('"ph": 1,')
        printer('"mt": 1')
        printer('},')
        printer('"value": ', 1.00000E+00, ',')
        printer('"initf": "",')
        printer('"processf": "",')
        printer('"calctype": "1"')
        printer('},')
        printer('{')
        printer('"id":', '"99998"', ',')
        printer('"corrgate": "0",')
        printer('"name": "', '<FALSE>', '",')
        printer('"evworkspacepair": {')
        printer('"ph": 1,')
        printer('"mt": 1')
        printer('},')
        printer('"value": ', 0.00000E+00, ',')
        printer('"initf": "",')
        printer('"processf": "",')
        printer('"calctype": "1"')
        printer('},')
        printer('{')
        printer('"id":', '"99997"', ',')
        printer('"corrgate": "0",')
        printer('"name": "', '<PASS>', '",')
        printer('"evworkspacepair": {')
        printer('"ph": 1,')
        printer('"mt": 1')
        printer('},')
        printer('"value": ', 1.00000E+00, ',')
        printer('"initf": "",')
        printer('"processf": "",')
        printer('"calctype": "1"')
        printer('},')
        printer('{')
        printer('"id":', '"99996"', ',')
        printer('"corrgate": "0",')
        printer('"name": "', "AUTOGENERATED", '",')
        printer('"evworkspacepair": {')
        printer('"ph": 1,')
        printer('"mt": 1')
        printer('},')
        printer('"value": ', 1.00000E+00, ',')
        printer('"initf": "",')
        printer('"processf": "",')
        printer('"calctype": "1"')
        printer('},')
        for basic_event in (self.non_ccf_events
        if self.ccf_groups else self.basic_events):
            basic_event.to_SAPHIRE_json_printer(printer)
        printer(']')
        printer('}')
        printer('}')

    def to_OpenPRA_json_printer(self, printer, nest=False):
        """Produces SAPHIRE JSON definition of the fault tree.

        The fault tree is produced breadth-first.
        The output SAPHIRE JSON representation is not formatted for human readability.
        The fault tree must be valid and well-formed.

        Args:
            printer: The output stream.
            nest: A nesting factor for the Boolean formulae.
        """
        printer('"basic_events": {')
        for basic_event in (self.non_ccf_events
                            if self.ccf_groups else self.basic_events):
            basic_event.to_OpenPRA_json_printer(printer)
        printer('},')
        printer('"house_events": {},')
        printer('"gates": {')

        sorted_gates = toposort_gates(self.top_gates or [self.top_gate],
                                      self.gates)
        for gate in sorted_gates:
            gate.to_OpenPRA_JSON_printer(printer, nest)
            if gate == sorted_gates[-1]:
                printer("}")
                printer("}")
                printer("},")
            else:
                printer("}")
                printer("},")
        # printer('}')
        printer('"components": {},')
        printer('"top_node": {')
        printer('"name": "80000",')
        printer('"reference_type": "gates",')
        printer('"tree_id": null,')
        printer('"path": "",')
        printer('"_proxy": "EventReference"')
        printer('},')
        printer('"name": "test2",')
        printer('"model_tree_id": null,')
        printer('"label": {')
        printer('"name": "test2",')
        printer('"description": ""')
        printer('}')
        printer('}')

    def to_SAPHIRE_json_object(self, base, nest=False):
        """Produces SAPHIRE JSON definition of the fault tree using the JSON python library.

        The fault tree is produced breadth-first.
        The output SAPHIRE JSON representation is not formatted for human readability.
        The fault tree must be valid and well-formed.

        Args:
            nest: A nesting factor for the Boolean formulae.
        """

        with open("output.json", "r") as f:
             base = json.load(f)

        sorted_gates = toposort_gates(self.top_gates or [self.top_gate],
                                      self.gates)
        for gate in sorted_gates:
            gateList = base['saphiresolveinput']['faulttreelist'][0]['gatelist']

            gate.to_SAPHIRE_JSON_object(base, nest)


        # for basic_event in (self.non_ccf_events
        #                     if self.ccf_groups else self.basic_events):
        #     basic_event.to_SAPHIRE_json_object(base)

        for basic_event in (self.non_ccf_events
                            if self.ccf_groups else self.basic_events):
            basic_event.to_SAPHIRE_json_object(base)

        for ccf_group in self.ccf_groups:
            ccf_group.to_SAPHIRE_json_object(base)
            ccf_group.to_SAPHIRE_json_ccf(base)
        #     # print("CCF",self.name)

        eventList = base['saphiresolveinput']['eventlist']
        with open("SAPHSOLVE_INPUT.JSInp", "w") as f:
            del gateList[1]
            del gateList[0]
            del eventList[4]
            json.dump(base, f, indent=4)

        with open("SAPHSOLVE_INPUT.JSInp", 'r') as f:
                base = json.load(f)
        def check_and_add_number(obj, num, add_num):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'eventinput' and num in value:
                        value.append(add_num)
                        obj['numinputs'] += 1
                    else:
                        check_and_add_number(value, num, add_num)
            elif isinstance(obj, list):
                for item in obj:
                    check_and_add_number(item, num, add_num)


        # instance = CcfGroup()
        # ccf_instance = ccf_instance.to_SAPHIRE_json_ccf(base)
        member_list =[]
        counter = []
        i = 1
        for ccf_group in self.ccf_groups:

            # ccf_group.to_SAPHIRE_json_object(base)
            # ccf_group.to_SAPHIRE_json_ccf(base)

            # first_group = self.ccf_groups[0]
            for member in ccf_group.members:
            # for member in first_group.members:
                print(member.name)
                check_and_add_number(base, int(member.name.strip("B")), int(ccf_group.name.strip("\"CCF") + "001"))
            # first_group = self.ccf_groups[]
            # for member in ccf_group.members[0]:
            #     print(member.name)
            # for ccf_g in ccf_group:
            #     print (ccf_g, member.name)
            # counter.append(i)
            # # i +=1
            # for i in ccf_group.name:
            #     print(i)
        # print("members", ccf_group.members.name)
        # print("counter", counter)
                # member_list=[member.name]
                # print(f"Index {member}: {ccf_g.name}")
                # print(member_list)
        # for i in counter:
        #     # check_and_add_number(base, member_list, int(ccf_group.name.strip("\"CCF") + "00000"))
        #     check_and_add_number(base, member_list, i + int("00000"))

        with open("SAPHSOLVE_INPUT.JSInp", 'w') as f:
            json.dump(base, f, indent = 4)

    def to_OpenPRA_json_printer(self, printer, nest=False):
        """Produces SAPHIRE JSON definition of the fault tree.

        The fault tree is produced breadth-first.
        The output SAPHIRE JSON representation is not formatted for human readability.
        The fault tree must be valid and well-formed.

        Args:
            printer: The output stream.
            nest: A nesting factor for the Boolean formulae.
        """
        printer('"basic_events": {')
        for basic_event in (self.non_ccf_events
                            if self.ccf_groups else self.basic_events):
            basic_event.to_OpenPRA_json_printer(printer)
        printer('},')
        printer('"house_events": {},')
        printer('"gates": {')

        sorted_gates = toposort_gates(self.top_gates or [self.top_gate],
                                      self.gates)
        for gate in sorted_gates:
            gate.to_OpenPRA_JSON_printer(printer, nest)
            if gate == sorted_gates[-1]:
                printer("}")
                printer("}")
                printer("},")
            else:
                printer("}")
                printer("},")
        # printer('}')
        printer('"components": {},')
        printer('"top_node": {')
        printer('"name": "80000",')
        printer('"reference_type": "gates",')
        printer('"tree_id": null,')
        printer('"path": "",')
        printer('"_proxy": "EventReference"')
        printer('},')
        printer('"name": "test2",')
        printer('"model_tree_id": null,')
        printer('"label": {')
        printer('"name": "test2",')
        printer('"description": ""')
        printer('}')
        printer('}')









def toposort_gates(root_gates, gates):
    """Sorts gates topologically starting from the root gate.

    The gate marks are used for the algorithm.
    After this sorting the marks are reset to None.

    Args:
        root_gates: The root gates of the graph.
        gates: Gates to be sorted.

    Returns:
        A deque of sorted gates.
    """
    for gate in gates:
        gate.mark = ""

    def visit(gate, final_list):
        """Recursively visits the given gate sub-tree to include into the list.

        Args:
            gate: The current gate.
            final_list: A deque of sorted gates.
        """
        assert gate.mark != "temp"
        if not gate.mark:
            gate.mark = "temp"
            for arg in gate.g_arguments:
                visit(arg, final_list)
            gate.mark = "perm"
            final_list.appendleft(gate)

    sorted_gates = deque()
    for root_gate in root_gates:
        visit(root_gate, sorted_gates)
    assert len(sorted_gates) == len(gates)
    for gate in gates:
        gate.mark = None
    return sorted_gates
