def distribute_house_events(fault_tree):
    """Distributes house events to already initialized gates.

    Args:
        fault_tree: The fault tree container of all events and constructs.
    """
    while len(fault_tree.house_events) < fault_tree.factors.num_house:
        target_gate = random.choice(fault_tree.gates)
        if (target_gate is not fault_tree.top_gate and
                target_gate.operator != "xor" and
                target_gate.operator != "not"):
            target_gate.add_argument(fault_tree.construct_house_event())