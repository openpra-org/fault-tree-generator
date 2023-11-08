import unittest
from fault_tree.event import HouseEvent
from fault_tree.event import Gate


class TestHouseEvent(unittest.TestCase):

    def test_house_event_initialization(self):
        """Test the initialization of a HouseEvent."""
        house_event_true = HouseEvent("TestEventTrue", "true")
        house_event_false = HouseEvent("TestEventFalse", "false")

        self.assertEqual(house_event_true.name, "TestEventTrue")
        self.assertEqual(house_event_true.state, "true")
        self.assertEqual(house_event_false.name, "TestEventFalse")
        self.assertEqual(house_event_false.state, "false")

    def test_house_event_str(self):
        """Test the string representation of a HouseEvent."""
        house_event = HouseEvent("TestEvent", "true")
        self.assertEqual(str(house_event), "TestEvent")

        house_event.state = "false"
        self.assertEqual(str(house_event), "TestEvent")

    def test_house_event_invalid_state(self):
        """Test the initialization of a HouseEvent with an invalid state."""
        with self.assertRaises(ValueError):
            HouseEvent("TestEventInvalid", "invalid_state")

    def test_house_event_state_change(self):
        """Test changing the state of a HouseEvent after initialization."""
        house_event = HouseEvent("TestEvent", "true")
        house_event.state = "false"
        self.assertEqual(house_event.state, "false")

        # Test setting an invalid state should raise a ValueError
        with self.assertRaises(ValueError):
            house_event.state = "invalid_state"

    def test_house_event_equality(self):
        event1 = HouseEvent(name="HE1", state="true")
        event2 = HouseEvent(name="HE1", state="true")
        self.assertEqual(event1, event2)

    def test_house_event_inequality(self):
        event1 = HouseEvent(name="HE1", state="true")
        event2 = HouseEvent(name="HE2", state="true")
        event3 = HouseEvent(name="HE1", state="false")
        self.assertNotEqual(event1, event2)
        self.assertEqual(event1, event3)

    def test_house_event_hash(self):
        event1 = HouseEvent(name="HE1", state="true")
        event2 = HouseEvent(name="HE1", state="true")
        self.assertEqual(hash(event1), hash(event2))

    def test_invalid_state(self):
        with self.assertRaises(ValueError):
            HouseEvent(name="HE1", state="invalid_state")

    def test_house_event_parent(self):
        event = HouseEvent(name="HE1", state="true")
        gate = Gate(name="G1", operator="AND")
        gate.add_house_event(event)
        self.assertIn(gate, event.parents)


if __name__ == '__main__':
    unittest.main()
