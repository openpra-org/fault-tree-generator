import unittest
from fault_tree.event.gate import Gate
from fault_tree.event.basic_event import BasicEvent
from fault_tree.event.house_event import HouseEvent
from fault_tree.probability.point_estimate import PointEstimate


class TestGate(unittest.TestCase):

    def test_gate_initialization(self):
        gate = Gate(name="G1", operator="AND")
        self.assertEqual(gate.name, "G1")
        self.assertEqual(gate.operator, "AND")
        self.assertIsNone(gate.k_num)

    def test_add_basic_events(self):
        gate = Gate(name="G1", operator="AND")
        basic_event = BasicEvent(name="BE1", probability=PointEstimate(0.1))
        gate.add_basic_event(basic_event)
        self.assertIn(basic_event, gate.b_arguments)
        self.assertIn(gate, basic_event.parents)

    def test_add_house_events(self):
        gate = Gate(name="G1", operator="AND")
        house_event = HouseEvent(name="HE1", state="true")
        gate.add_house_event(house_event)
        self.assertIn(house_event, gate.h_arguments)
        self.assertIn(gate, house_event.parents)

    def test_add_gates(self):
        parent_gate = Gate(name="G1", operator="AND")
        child_gate = Gate(name="G2", operator="OR")
        parent_gate.add_gate(child_gate)
        self.assertIn(child_gate, parent_gate.g_arguments)
        self.assertIn(parent_gate, child_gate.parents)

    def test_num_arguments(self):
        gate = Gate(name="G1", operator="AND")
        basic_event = BasicEvent(name="BE1", probability=PointEstimate(0.1))
        house_event = HouseEvent(name="HE1", state="true")
        child_gate = Gate(name="G2", operator="OR")
        gate.add_basic_event(basic_event)
        gate.add_house_event(house_event)
        gate.add_gate(child_gate)
        self.assertEqual(gate.num_arguments(), 3)

    def test_gate_equality(self):
        gate1 = Gate(name="G1", operator="AND")
        gate2 = Gate(name="G1", operator="AND")
        self.assertEqual(gate1, gate2)

    def test_gate_inequality(self):
        gate1 = Gate(name="G1", operator="AND")
        gate2 = Gate(name="G2", operator="AND")
        gate3 = Gate(name="G1", operator="OR")
        self.assertNotEqual(gate1, gate2)
        self.assertEqual(gate1, gate3)

    def test_gate_hash(self):
        gate1 = Gate(name="G1", operator="AND")
        gate2 = Gate(name="G1", operator="AND")
        self.assertEqual(hash(gate1), hash(gate2))

    def test_add_duplicate_events(self):
        gate = Gate(name="G1", operator="AND")
        basic_event = BasicEvent(name="BE1", probability=PointEstimate(0.1))
        gate.add_basic_event(basic_event)
        with self.assertRaises(AssertionError):
            gate.add_basic_event(basic_event)

    def test_get_ancestors(self):
        parent_gate = Gate(name="G1", operator="AND")
        child_gate = Gate(name="G2", operator="OR")
        parent_gate.add_gate(child_gate)
        ancestors = child_gate.get_ancestors()
        self.assertIn(parent_gate, ancestors)
        self.assertIn(child_gate, ancestors)


if __name__ == '__main__':
    unittest.main()