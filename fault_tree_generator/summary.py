# def write_info(fault_tree, printer, seed):
#     """Writes the information about the setup for fault tree generation.
#
#     Args:
#         fault_tree: A full, valid, well-formed fault tree.
#         printer: The output stream.
#         seed: The seed of the pseudo-random number generator.
#     """
#     factors = fault_tree.factors
#     printer('<?xml version="1.0"?>')
#     printer('<!--')
#     printer('This is a description of the auto-generated fault tree')
#     printer('with the following parameters:\n')
#     printer('The fault tree name: ', fault_tree.name)
#     printer('The root gate name: ', fault_tree.top_gate.name)
#     printer()
#     printer('The seed of the random number generator: ', seed)
#     printer('The number of basic events: ', factors.num_basic)
#     printer('The number of house events: ', factors.num_house)
#     printer('The number of CCF groups: ', factors.num_ccf)
#     printer('The average number of gate arguments: ', factors.num_args)
#     printer('The weights of gate types [AND, OR, K/N, NOT, XOR]: ',
#             factors.get_gate_weights())
#     printer('Percentage of common basic events per gate: ', factors.common_b)
#     printer('Percentage of common gates per gate: ', factors.common_g)
#     printer('The avg. number of parents for common basic events: ',
#             factors.parents_b)
#     printer('The avg. number of parents for common gates: ', factors.parents_g)
#     printer('Maximum probability for basic events: ', factors.max_prob)
#     printer('Minimum probability for basic events: ', factors.min_prob)
#     printer('-->')
#
#
#
#     printer('The number of basic events: ', factors.num_basic)
#     printer('The number of house events: ', factors.num_house)
#     printer('The number of CCF groups: ', factors.num_ccf)
#     printer('The average number of gate arguments: ', factors.num_args)
#     printer('The weights of gate types [AND, OR, K/N, NOT, XOR]: ',
#             factors.get_gate_weights())
#     printer('Percentage of common basic events per gate: ', factors.common_b)
#     printer('Percentage of common gates per gate: ', factors.common_g)
#     printer('The avg. number of parents for common basic events: ',
#             factors.parents_b)
#     printer('The avg. number of parents for common gates: ', factors.parents_g)
#     printer('Maximum probability for basic events: ', factors.max_prob)
#     printer('Minimum probability for basic events: ', factors.min_prob)
#
#
# def write_summary(fault_tree, printer):
#     """Writes the summary of the generated fault tree.
#
#     Args:
#         fault_tree: A full, valid, well-formed fault tree.
#         printer: The output stream.
#     """
#     printer('<!--\nThe generated fault tree has the following metrics:\n')
#     get_size_summary(fault_tree, printer)
#     get_complexity_summary(fault_tree, printer)
#     printer('-->\n')