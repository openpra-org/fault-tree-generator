def candidate_gates(common_gate):
    """Lazy generator of candidates for common gates.

    Args:
        common_gate: A list of common gates.

    Yields:
        A next gate candidate from common gates container.
    """
    orphans = [x for x in common_gate if not x.parents]
    random.shuffle(orphans)
    for i in orphans:
        # print(i)
        yield i

    single_parent = [x for x in common_gate if len(x.parents) == 1]
    random.shuffle(single_parent)
    for i in single_parent:
        # print(i)
        yield i

    multi_parent = [x for x in common_gate if len(x.parents) > 1]
    random.shuffle(multi_parent)
    for i in multi_parent:
        # print(i)
        yield i