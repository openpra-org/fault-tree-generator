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

# from ordered_set import OrderedSet

from collections import deque

from event.basic_event import BasicEvent
from event.gate import Gate
from event.house_event import HouseEvent


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
        assert self.model == "MGL"
        assert self.factors
        level = 2
        for factor in self.factors:
            printer('<factor level="', level, '">')
            printer('<float value="', factor, '"/>')
            printer('</factor>')
            level += 1
        printer('</factors>')

        printer('</define-CCF-group>')


class FaultTree(object):  # pylint: disable=too-many-instance-attributes
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
        self.gates: OrderedSet[Gate] = OrderedSet()
        self.basic_events: OrderedSet[BasicEvent] = OrderedSet()
        self.house_events: OrderedSet[HouseEvent] = OrderedSet()
        self.ccf_groups: OrderedSet[CcfGroup] = OrderedSet()
        self.non_ccf_events = OrderedSet()  # must be assigned directly.

    def __getstate__(self):
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

    def __setstate__(self, state):
        self.name = state['name']
        self.top_gate = state['top_gate']
        self.top_gates = state['top_gates']
        self.gates: OrderedSet[Gate] = state['gates']
        self.basic_events: OrderedSet[BasicEvent] = state['basic_events']
        self.house_events: OrderedSet[HouseEvent] = state['house_events']
        self.ccf_groups: OrderedSet[CcfGroup] = state['ccf_groups']
        self.non_ccf_events = state['non_ccf_events']

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

        for gate in self.gates:
            gate.to_xml(printer, nest)

        for ccf_group in self.ccf_groups:
            ccf_group.to_xml(printer)
        printer('</define-fault-tree>')

        printer('<model-data>')
        for basic_event in (self.non_ccf_events if self.ccf_groups else self.basic_events):
            basic_event.to_xml(printer)

        for house_event in self.house_events:
            house_event.to_xml(printer)
        printer('</model-data>')
        printer('</opsa-mef>')

    def add_gates(self, gates: OrderedSet[Gate], shallow=False):
        self.gates.update(gates)
        if not shallow:
            for gate in gates:
                self.basic_events.update(gate.b_arguments)
                self.house_events.update(gate.h_arguments)
                self.add_gates(gates=gate.g_arguments, shallow=False)

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

    def prune(self, gate: Gate):
        if gate.num_arguments() == 1:
            # Unexpected number of parents
            if gate.num_parents() > 1:
                print('Unexpected number of parents for gate ' + gate.name)
            elif gate.num_parents() > 0:
                parent: Gate = gate.parents.pop()
                parent.g_arguments.remove(gate)
                for x in gate.g_arguments:
                    parent.add_argument(x)
                for x in gate.b_arguments:
                    parent.add_argument(x)
                for x in gate.h_arguments:
                    parent.add_argument(x)
                for x in gate.u_arguments:
                    parent.add_argument(x)
                self.gates.remove(gate)
                for gate in gate.g_arguments:
                    self.prune(gate)


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
