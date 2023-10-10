def choose_basic_event(s_common, common_basic, fault_tree):
    """Creates a new basic event or uses a common one for gate arguments.

    Args:
        s_common: Sampled factor to choose common basic events.
        common_basic: A list of common basic events to choose from.
        fault_tree: The fault tree container of all events and constructs.

    Returns:
        Basic event argument for a gate.
    """
    if s_common >= fault_tree.factors.common_b or not common_basic:
        return fault_tree.construct_basic_event()

    orphans = [x for x in common_basic if not x.parents]
    if orphans:
        return random.choice(orphans)

    single_parent = [x for x in common_basic if len(x.parents) == 1]
    if single_parent:
        return random.choice(single_parent)

    return random.choice(common_basic)