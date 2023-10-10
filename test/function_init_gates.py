def init_gates(gates_queue, common_basic, common_gate, fault_tree):
    """Initializes gates and other basic events.

    Args:
        gates_queue: A deque of gates to be initialized.
        common_basic: A list of common basic events.
        common_gate: A list of common gates.
        fault_tree: The fault tree container of all events and constructs.
    """
    # Get an intermediate gate to initialize breadth-first
    # print(len(fault_tree.basic_events))
    gate = gates_queue.popleft()
    # print(gate)
    num_arguments = fault_tree.factors.get_num_args(gate)
    # print(num_arguments)
    # print(gate.num_arguments())
    ancestors = None  # needed for cycle prevention
    max_tries = len(common_gate)  # the number of maximum tries
    num_tries = 0  # the number of tries to get a common gate

    # pylint: disable=too-many-nested-blocks
    # This code is both hot and coupled for performance reasons.
    # There may be a better solution than the current approach.
    while gate.num_arguments() < num_arguments:
        s_percent = random.random()  # sample percentage of gates
        s_common = random.random()  # sample the reuse frequency

        # Case when the number of basic events is already satisfied
        if len(fault_tree.basic_events) == fault_tree.factors.num_basic:
            s_common = 0  # use only common nodes

        if s_percent < fault_tree.factors.get_percent_gate():
            # Create a new gate or use a common one
            if s_common < fault_tree.factors.common_g and num_tries < max_tries:
                # Lazy evaluation of ancestors
                if not ancestors:
                    ancestors = gate.get_ancestors()

                for random_gate in candidate_gates(common_gate):
                    num_tries += 1
                    if num_tries >= max_tries:
                        break
                    if random_gate in gate.g_arguments or random_gate is gate:
                        continue
                    if (not random_gate.g_arguments or
                            random_gate not in ancestors):
                        if not random_gate.parents:
                            gates_queue.append(random_gate)
                        gate.add_argument(random_gate)
                        break
            else:
                new_gate = fault_tree.construct_gate()
                gate.add_argument(new_gate)
                gates_queue.append(new_gate)
        else:
            gate.add_argument(
                choose_basic_event(s_common, common_basic, fault_tree))

    correct_for_exhaustion(gates_queue, common_gate, fault_tree)