import json
from typing import Dict, Tuple
from fault_tree import FaultTree


def size_summary(fault_tree: FaultTree) -> Dict[str, any]:
    """Gathers information about the size of the fault tree.

    Args:
        fault_tree: A full, valid, well-formed fault tree.

    Returns:
        dict: A dictionary containing the size summary of the fault tree.
    """
    gate_count = {'and': 0, 'or': 0, 'atleast': 0, 'not': 0, 'xor': 0}
    for gate in fault_tree.gates:
        gate_count[gate.operator] += 1

    summary = {
        'basic_events': len(fault_tree.basic_events),
        'house_events': len(fault_tree.house_events),
        'ccf_groups': len(fault_tree.ccf_groups),
        'total_gates': len(fault_tree.gates),
        'gate_types': {
            'and': gate_count['and'],
            'or': gate_count['or'],
            'atleast': gate_count['atleast'],
            'not': gate_count['not'],
            'xor': gate_count['xor']
        }
    }

    return summary


def size_summary_json(fault_tree: FaultTree, indent: int = 4, **kwargs) -> str:
    """Serializes the size summary of the fault tree into a JSON string.

    Args:
        fault_tree: A full, valid, well-formed fault tree.
        indent (int, optional): Indentation level for pretty-printing the JSON output.
                                Defaults to 4.
        **kwargs: Additional keyword arguments to pass to json.dumps().

    Returns:
        str: A JSON string containing the size summary of the fault tree.
    """
    return json.dumps(size_summary(fault_tree), indent=indent, **kwargs)


def calculate_event_proportions(fault_tree: FaultTree) -> Dict[str, Dict[str, float]]:
    """Computes the proportions of basic and common events in gate arguments.

    This method calculates three different proportions that provide insights into
    the composition and connectivity of the fault tree's gates:

    - The average fraction of basic event arguments per gate, which indicates the
      proportion of basic events in the arguments of a gate.
    - The average fraction of common basic events among all basic event arguments
      per gate, which reflects the redundancy of basic events in the fault tree.
    - The average fraction of common gates among all gate arguments per gate,
      which shows the interconnectivity and sharing of gates in the fault tree.

    Args:
        fault_tree: A full, valid, well-formed fault tree.

    Returns:
        Tuple containing:
        - frac_b (float): The average fraction of basic event arguments per gate.
                          This value ranges from 0 to 1, where 0 indicates no basic
                          event arguments and 1 indicates all arguments are basic events.
        - common_b (float): The average fraction of common basic events among all
                            basic event arguments per gate. This value ranges from 0 to 1,
                            where 0 indicates no commonality and 1 indicates all basic
                            event arguments are common.
        - common_g (float): The average fraction of common gates among all gate
                            arguments per gate. This value ranges from 0 to 1, where 0
                            indicates no commonality and 1 indicates all gate arguments
                            are common.

    Note:
        These proportions are independent metrics and are not expected to sum to 1.
        They are calculated as averages across all gates in the fault tree.
    """
    frac_b = 0.0
    common_b = 0.0
    common_g = 0.0
    for gate in fault_tree.gates:
        num_b_arguments = len(gate.b_arguments)
        num_g_arguments = len(gate.g_arguments)
        total_arguments = num_g_arguments + num_b_arguments
        frac_b += num_b_arguments / total_arguments if total_arguments else 0
        if gate.b_arguments:
            num_common_b = len([x for x in gate.b_arguments if x.is_common()])
            common_b += num_common_b / num_b_arguments
        if gate.g_arguments:
            num_common_g = len([x for x in gate.g_arguments if x.is_common()])
            common_g += num_common_g / num_g_arguments

    num_gates_with_b = len([x for x in fault_tree.gates if x.b_arguments])
    num_gates_with_g = len([x for x in fault_tree.gates if x.g_arguments])
    frac_b /= len(fault_tree.gates) if fault_tree.gates else 1
    common_b /= num_gates_with_b if num_gates_with_b else 1
    common_g /= num_gates_with_g if num_gates_with_g else 1

    return {
        "fractions": {
            "basic_events": frac_b,
            "common_basic_events": common_b,
            "common_gates": common_g
        }
    }


def get_complexity_summary(fault_tree, printer):
    """Gathers information about the complexity factors of the fault tree.

    Args:
        fault_tree: A full, valid, well-formed fault tree.
        printer: The output stream.
    """
    frac_b, common_b, common_g = calculate_event_proportions(fault_tree)
    shared_b = [x for x in fault_tree.basic_events if x.is_common()]
    shared_g = [x for x in fault_tree.gates if x.is_common()]

    printer('Basic events to gates ratio: ', (len(fault_tree.basic_events) / len(fault_tree.gates)))
    printer('The average number of gate arguments: ', (sum(x.num_arguments() for x in fault_tree.gates) / len(fault_tree.gates)))
    printer('The number of common basic events: ', len(shared_b))
    printer('The number of common gates: ', len(shared_g))
    printer('Percentage of common basic events per gate: ', common_b)
    printer('Percentage of common gates per gate: ', common_g)
    printer('Percentage of arguments that are basic events per gate: ', frac_b)
    if shared_b:
        printer('The avg. number of parents for common basic events: ', (sum(x.num_parents() for x in shared_b) / len(shared_b)))
    if shared_g:
        printer('The avg. number of parents for common gates: ', (sum(x.num_parents() for x in shared_g) / len(shared_g)))