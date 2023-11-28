import unittest
from fault_tree.event.basic_event import BasicEvent
from fault_tree.probability.point_estimate import PointEstimate
from ordered_set import OrderedSet
from pyeda.inter import exprvar


class TestBasicEvent(unittest.TestCase):

    def test_basic_event_initialization_with_probability(self):
        probability = PointEstimate(0.1)
        event = BasicEvent(name="BE1", probability=probability)
        self.assertEqual(event.name, "BE1")
        self.assertEqual(event.probability, probability)

    def test_basic_event_initialization_without_probability(self):
        event = BasicEvent(name="BE1", probability=None)
        self.assertEqual(event.name, "BE1")
        self.assertIsNone(event.probability)

    def test_basic_event_probability_getter_setter(self):
        probability = PointEstimate(0.1)
        event = BasicEvent(name="BE1", probability=probability)
        new_probability = PointEstimate(0.2)
        event.probability = new_probability
        self.assertEqual(event.probability, new_probability)

    def test_basic_event_str(self):
        probability = PointEstimate(0.1)
        event = BasicEvent(name="BE1", probability=probability)
        self.assertEqual(str(event), "BE1")

    def test_basic_event_equality(self):
        probability = PointEstimate(0.1)
        event1 = BasicEvent(name="BE1", probability=probability)
        event2 = BasicEvent(name="BE1", probability=probability)
        self.assertEqual(event1, event2)

    def test_basic_event_inequality(self):
        probability = PointEstimate(0.1)
        event1 = BasicEvent(name="BE1", probability=probability)
        event2 = BasicEvent(name="BE2", probability=probability)
        event3 = BasicEvent(name="BE1", probability=PointEstimate(0.2))
        self.assertNotEqual(event1, event2)
        self.assertEqual(event1, event3)

    def test_basic_event_hash(self):
        probability = PointEstimate(0.1)
        event1 = BasicEvent(name="BE1", probability=probability)
        event2 = BasicEvent(name="BE1", probability=probability)
        self.assertEqual(hash(event1), hash(event2))

    def test_invalid_probability_assignment(self):
        event = BasicEvent(name="BE1", probability=None)
        with self.assertRaises(TypeError):
            event.probability = "not_a_probability_instance"

    def test_to_bdd_with_no_var_order(self):
        """Test that to_bdd() returns the correct BDD variable when no var_order is provided."""
        event_name = "BE1"
        basic_event = BasicEvent(name=event_name, probability=PointEstimate(0.1))
        bdd = basic_event.to_bdd()
        expected_bdd = exprvar(event_name)
        self.assertEqual(bdd, expected_bdd)

    def test_to_bdd_with_var_order(self):
        """Test that to_bdd() respects the var_order when provided."""
        event_name = "BE2"
        basic_event = BasicEvent(name=event_name, probability=PointEstimate(0.1))
        var_order = OrderedSet(["BE3", "BE2", "BE1"])
        bdd = basic_event.to_bdd(var_order=var_order)
        expected_bdd = exprvar('x1')  # Assuming 'x1' is the correct variable name based on the index
        self.assertEqual(bdd, expected_bdd)

    def test_to_bdd_with_var_order_not_including_event(self):
        """Test that to_bdd() returns the correct BDD variable when var_order does not include the event."""
        event_name = "BE4"
        basic_event = BasicEvent(name=event_name, probability=PointEstimate(0.1))
        var_order = OrderedSet(["BE3", "BE1"])
        bdd = basic_event.to_bdd(var_order=var_order)
        expected_bdd = exprvar(event_name)
        self.assertEqual(bdd, expected_bdd)

    def test_to_bdd_with_empty_var_order(self):
        """Test that to_bdd() returns the correct BDD variable when an empty var_order is provided."""
        event_name = "BE5"
        basic_event = BasicEvent(name=event_name, probability=PointEstimate(0.1))
        var_order = OrderedSet()
        bdd = basic_event.to_bdd(var_order=var_order)
        expected_bdd = exprvar(event_name)
        self.assertEqual(bdd, expected_bdd)

if __name__ == '__main__':
    unittest.main()
