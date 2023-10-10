def generate_ccf_groups(fault_tree):
    """Creates CCF groups from the existing basic events.

    Args:
        fault_tree: The fault tree container of all events and constructs.
    """
    if fault_tree.factors.num_ccf:
        num_ccf_total = fault_tree.factors.num_ccf
        # print("num_ccf", num_ccf_total)
        members = fault_tree.basic_events[:]
        # print("members", len(members))
        random.shuffle(members)
        first_mem = 0
        last_mem = 0
        while len(fault_tree.ccf_groups) < fault_tree.factors.num_ccf:
            max_args = int(2 * fault_tree.factors.num_args - 2)
            max_args = fault_tree.factors.ccf_size
            # print(max_args)
            group_size = random.randint(2, max_args)
            # print(group_size)
            last_mem = first_mem + group_size
            if last_mem > len(members):
                break
            fault_tree.construct_ccf_group(members[first_mem:last_mem])
            # print("fir",members)
            first_mem = last_mem
        fault_tree.non_ccf_events = members[first_mem:]