import unittest
from fault_tree import FaultTree, CCFGroup
from fault_tree.event import Gate, BasicEvent, HouseEvent
from ordered_set import OrderedSet


class TestFaultTree(unittest.TestCase):

    def setUp(self):
        # Set up a basic fault tree structure for use in multiple tests
        self.ft = FaultTree(name="TestTree")
        self.gate1 = Gate(name="G1", operator="AND")
        self.gate2 = Gate(name="G2", operator="OR")
        self.basic_event1 = BasicEvent(name="BE1", probability=None)
        self.basic_event2 = BasicEvent(name="BE2", probability=None)
        self.house_event1 = HouseEvent(name="HE1", state="true")

    def test_initialization(self):
        # Test initialization of the fault tree
        self.assertEqual(self.ft.name, "TestTree")
        self.assertIsNone(self.ft.top_gate)
        self.assertIsNone(self.ft.top_gates)
        self.assertEqual(len(self.ft.gates), 0)
        self.assertEqual(len(self.ft.basic_events), 0)
        self.assertEqual(len(self.ft.house_events), 0)
        self.assertEqual(len(self.ft.ccf_groups), 0)
        self.assertEqual(len(self.ft.non_ccf_events), 0)

    def test_add_gates(self):
        # Test adding gates to the fault tree
        self.ft.add_gates(OrderedSet([self.gate1, self.gate2]))
        self.assertIn(self.gate1, self.ft.gates)
        self.assertIn(self.gate2, self.ft.gates)
        self.assertEqual(len(self.ft.gates), 2)

    def test_add_gates_with_arguments(self):
        # Test adding gates with arguments (basic and house events)
        self.gate1.add_argument(self.basic_event1)
        self.gate2.add_argument(self.house_event1)
        self.ft.add_gates(OrderedSet([self.gate1, self.gate2]))
        self.assertIn(self.basic_event1, self.ft.basic_events)
        self.assertIn(self.house_event1, self.ft.house_events)

    def test_prune_single_argument_gate(self):
        # Test pruning a gate with a single argument
        self.gate1.add_argument(self.basic_event1)
        self.ft.add_gates(OrderedSet([self.gate1]))
        self.ft.prune(self.gate1)
        self.assertNotIn(self.gate1, self.ft.gates)
        self.assertIn(self.basic_event1, self.ft.basic_events)

    def test_prune_gate_with_multiple_parents(self):
        # Test pruning a gate with multiple parents (should raise an exception)
        self.gate1.add_argument(self.basic_event1)
        self.gate2.add_argument(self.gate1)
        self.ft.add_gates(OrderedSet([self.gate1, self.gate2]))
        with self.assertRaises(ValueError):
            self.ft.prune(self.gate1)

    def test_getstate_setstate(self):
        # Test the serialization and deserialization of the fault tree (getstate and setstate)
        self.ft.add_gates(OrderedSet([self.gate1, self.gate2]))
        state = self.ft.__getstate__()
        new_ft = FaultTree()
        new_ft.__setstate__(state)
        self.assertEqual(new_ft.gates, self.ft.gates)
        self.assertEqual(new_ft.basic_events, self.ft.basic_events)
        self.assertEqual(new_ft.house_events, self.ft.house_events)

    # Additional tests can be added here to cover more scenarios and corner cases


if __name__ == '__main__':
    unittest.main()