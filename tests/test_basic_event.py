import unittest
from fault_tree.event.basic_event import BasicEvent
from fault_tree.probability.point_estimate import PointEstimate


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


if __name__ == '__main__':
    unittest.main()
