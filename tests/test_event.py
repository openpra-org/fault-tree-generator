import unittest
from ordered_set import OrderedSet
from fault_tree.event import Event


# Mocking the Gate class for testing purposes
class MockGate:
    def __init__(self, name):
        self.name = name


class TestEvent(unittest.TestCase):

    def test_event_initialization(self):
        """Test the initialization of an Event."""
        event = Event("TestEvent")
        self.assertEqual(event.name, "TestEvent")
        self.assertIsInstance(event.parents, OrderedSet)
        self.assertEqual(len(event.parents), 0)

    def test_event_str(self):
        """Test the string representation of an Event."""
        event = Event("TestEvent")
        self.assertEqual(str(event), "TestEvent")

        event_no_name = Event()
        self.assertEqual(str(event_no_name), "")

    def test_event_hash(self):
        """Test the hashability of an Event."""
        event = Event("TestEvent")
        event_same_name = Event("TestEvent")
        event_diff_name = Event("AnotherEvent")

        self.assertEqual(hash(event), hash(event_same_name))
        self.assertNotEqual(hash(event), hash(event_diff_name))

    def test_event_equality(self):
        """Test the equality method of an Event."""
        event = Event("TestEvent")
        event_same_name = Event("TestEvent")
        event_diff_name = Event("AnotherEvent")
        non_event = "NotAnEvent"

        self.assertEqual(event, event_same_name)
        self.assertNotEqual(event, event_diff_name)
        self.assertNotEqual(event, non_event)

    def test_event_is_common(self):
        """Test if an Event is common (has multiple parents)."""
        event = Event("TestEvent")
        gate1 = MockGate("Gate1")
        gate2 = MockGate("Gate2")

        self.assertFalse(event.is_common())

        event.add_parent(gate1)
        self.assertFalse(event.is_common())

        event.add_parent(gate2)
        self.assertTrue(event.is_common())

    def test_event_is_orphan(self):
        """Test if an Event is an orphan (has no parents)."""
        event = Event("TestEvent")
        gate = MockGate("Gate1")

        self.assertTrue(event.is_orphan())

        event.add_parent(gate)
        self.assertFalse(event.is_orphan())

    def test_event_num_parents(self):
        """Test the number of parents of an Event."""
        event = Event("TestEvent")
        gate1 = MockGate("Gate1")
        gate2 = MockGate("Gate2")

        self.assertEqual(event.num_parents(), 0)

        event.add_parent(gate1)
        self.assertEqual(event.num_parents(), 1)

        event.add_parent(gate2)
        self.assertEqual(event.num_parents(), 2)

    def test_event_add_parent(self):
        """Test adding a parent to an Event."""
        event = Event("TestEvent")
        gate = MockGate("Gate1")

        event.add_parent(gate)
        self.assertIn(gate, event.parents)

        # Test adding the same parent again should raise an AssertionError
        with self.assertRaises(AssertionError):
            event.add_parent(gate)


if __name__ == '__main__':
    unittest.main()