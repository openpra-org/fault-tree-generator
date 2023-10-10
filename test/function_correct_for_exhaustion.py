def correct_for_exhaustion(gates_queue, common_gate, fault_tree):
    """Corrects the generation for queue exhaustion.

    Corner case when not enough new basic events initialized,
    but there are no more intermediate gates to use
    due to a big ratio or just random accident.

    Args:
        gates_queue: A deque of gates to be initialized.
        common_gate: A list of common gates.
        fault_tree: The fault tree container of all events and constructs.
    """
    if gates_queue:
        return
    if len(fault_tree.basic_events) < fault_tree.factors.num_basic:
        # Initialize one more gate
        # by randomly choosing places in the fault tree.
        random_gate = random.choice(fault_tree.gates)
        while (random_gate.operator == "not" or random_gate.operator == "xor" or
               random_gate in common_gate):
            random_gate = random.choice(fault_tree.gates)
        new_gate = fault_tree.construct_gate()
        random_gate.add_argument(new_gate)
        gates_queue.append(new_gate)