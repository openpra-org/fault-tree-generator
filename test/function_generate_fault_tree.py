def generate_fault_tree(ft_name, root_name, factors):
    """Generates a fault tree of specified complexity.

    The Factors class attributes are used as parameters for complexity.

    Args:
        ft_name: The name of the fault tree.
        root_name: The name for the root gate of the fault tree.
        factors: Factors for fault tree generation.

    Returns:
        Top gate of the created fault tree.
    """
    fault_tree = GeneratorFaultTree(ft_name, factors)
    fault_tree.construct_top_gate(root_name)

    # Estimating the parameters
    num_gate = factors.get_num_gate()
    num_basic_events = factors.num_basic
    num_common_basic = factors.get_num_common_basic(num_gate)
    num_common_gate = factors.get_num_common_gate(num_gate)
    common_basic = [
        fault_tree.construct_basic_event() for _ in range(num_common_basic)
    ]
    common_gate = [fault_tree.construct_gate() for _ in range(num_common_gate)]

    # Container for not yet initialized gates
    # A deque is used to traverse the tree breadth-first
    gates_queue = deque()
    gates_queue.append(fault_tree.top_gate)
    while gates_queue:
        init_gates(gates_queue, common_basic, common_gate, fault_tree)

    assert (not [x for x in fault_tree.basic_events if x.is_orphan()])
    assert (not [
        x for x in fault_tree.gates
        if x.is_orphan() and x is not fault_tree.top_gate
    ])

    distribute_house_events(fault_tree)
    generate_ccf_groups(fault_tree)
    return fault_tree