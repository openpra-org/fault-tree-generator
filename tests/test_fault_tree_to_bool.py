import unittest
from pyeda.inter import exprvar, And, Not, Or, expr, expr2bdd, bddvars
from fault_tree.event import BasicEvent, Gate, HouseEvent
from fault_tree.fault_tree import FaultTree
from fault_tree.probability import PointEstimate
from ordered_set import OrderedSet


class TestFaultTreeToBoolean(unittest.TestCase):

    def setUp(self):
        # Create basic events
        self.be1 = BasicEvent(name="BE1", probability=None)
        self.be2 = BasicEvent(name="BE2", probability=None)
        self.be3 = BasicEvent(name="BE3", probability=None)

        # Create house events
        self.he1 = HouseEvent(name="HE1", state="true")
        self.he2 = HouseEvent(name="HE2", state="false")

        # Create gates
        self.gate_and = Gate(name="G_AND", operator="and")
        self.gate_or = Gate(name="G_OR", operator="or")
        self.gate_not = Gate(name="G_NOT", operator="not")

        # Add basic and house events to gates
        self.gate_and.add_basic_event(self.be1)
        self.gate_and.add_basic_event(self.be2)
        self.gate_or.add_basic_event(self.be2)
        self.gate_or.add_house_event(self.he1)
        self.gate_not.add_basic_event(self.be3)

        # Create a top-level gate and add sub-gates
        self.top_gate = Gate(name="TOP", operator="or")
        self.top_gate.add_gate(self.gate_and)
        self.top_gate.add_gate(self.gate_or)
        self.top_gate.add_gate(self.gate_not)

        # Create a fault tree and set the top gate
        self.fault_tree = FaultTree(name="TestTree")
        self.fault_tree.top_gate = self.top_gate

    def test_to_boolean(self):
        # Get the boolean expression, PyEDA expression, and BDD from the fault tree
        boolean_expr, pyeda_expr, bdd = self.fault_tree.to_boolean()

        # Expected boolean expression, adjusted to match the format produced by to_boolean()
        expected_boolean_expr = "((BE1 & BE2) | (BE2 | HE1) | ~BE3)"

        # Check if the boolean expression matches the expected expression
        self.assertEqual(boolean_expr, expected_boolean_expr)

        # Check if the PyEDA expression is equivalent to the expected expression
        expected_pyeda_expr = Or(And(exprvar('BE1'), exprvar('BE2')), Or(exprvar('BE2'), exprvar('HE1')),
                                 Not(exprvar('BE3')))
        self.assertTrue(pyeda_expr.equivalent(expected_pyeda_expr),
                        "PyEDA expression is not equivalent to the expected expression.")

        # Create BDD variables in the desired order
        # Create BDD variables in the desired order
        exprvar('BE1')
        exprvar('BE2')
        exprvar('HE1')
        exprvar('BE3')

        # Convert the expected PyEDA expression to a BDD
        expected_bdd = expr2bdd(expected_pyeda_expr)

        # Check if the BDD is equivalent to the expected BDD
        self.assertTrue(bdd.equivalent(expected_bdd), "BDD is not equivalent to the expected BDD.")

        # Additional debugging information
        print("Boolean Expression:", boolean_expr)
        print("Expected PyEDA Expression:", expected_pyeda_expr)
        print("Actual PyEDA Expression:", pyeda_expr)
        print("Expected BDD:", expected_bdd)
        print("Actual BDD:", bdd)

    def test_to_boolean_with_order(self):
        # Define a specific variable order
        var_order = OrderedSet(['BE3', 'BE1', 'BE2', 'HE1'])

        # Get the boolean expression, PyEDA expression, and BDD with the specified variable order
        boolean_expr, pyeda_expr, bdd = self.fault_tree.to_boolean(var_order=var_order)

        # Expected boolean expression remains the same
        expected_boolean_expr = "((BE1 & BE2) | (BE2 | HE1) | ~BE3)"

        # Check if the boolean expression matches the expected expression
        self.assertEqual(boolean_expr, expected_boolean_expr)

        # Check if the PyEDA expression is equivalent to the expected expression
        expected_pyeda_expr = Or(And(exprvar('BE1'), exprvar('BE2')), Or(exprvar('BE2'), exprvar('HE1')),
                                 Not(exprvar('BE3')))
        self.assertTrue(pyeda_expr.equivalent(expected_pyeda_expr),
                        "PyEDA expression is not equivalent to the expected expression.")

        # Create BDD variables in the specified order
        for var in var_order:
            exprvar(var)

        # Convert the expected PyEDA expression to a BDD with the specified variable order
        expected_bdd = expr2bdd(expected_pyeda_expr, ordering=var_order)

        # Check if the BDD is equivalent to the expected BDD
        self.assertTrue(bdd.equivalent(expected_bdd), "BDD is not equivalent to the expected BDD.")

        # Additional debugging information
        print("Variable Order:", var_order)
        print("Boolean Expression:", boolean_expr)
        print("Expected PyEDA Expression:", expected_pyeda_expr)
        print("Actual PyEDA Expression:", pyeda_expr)
        print("Expected BDD:", expected_bdd)
        print("Actual BDD:", bdd)


if __name__ == '__main__':
    unittest.main()