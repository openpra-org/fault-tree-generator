import sys
import random
import argparse

from fault_tree_generator import ComplexityFactorError, GenerativeFaultTree
from fault_tree_generator import FaultTreeGeneratorArgParser, ComplexityFactors


def setup_factors(parsed_args):
    """Configures the fault generation by assigning factors.

    Args:
        parsed_args: Command-line arguments with values for factors.

    Returns:
        Fully initialized Factors object.

    Raises:
        ArgumentTypeError: Problems with the arguments.
        FactorError: Invalid setup for factors.
    """
    random.seed(parsed_args.seed)

    complexity_factors = ComplexityFactors()

    complexity_factors.set_min_max_prob(parsed_args.min_prob, parsed_args.max_prob)

    complexity_factors.set_common_event_factors(parsed_args.common_b, parsed_args.common_g,
                                                parsed_args.parents_b, parsed_args.parents_g)

    complexity_factors.set_num_factors(parsed_args.num_args, parsed_args.num_basic, parsed_args.num_house,
                                       parsed_args.num_ccf)

    complexity_factors.set_gate_weights([float(i) for i in parsed_args.weights_g])

    if parsed_args.num_gate:
        complexity_factors.constrain_num_gate(parsed_args.num_gate)

    complexity_factors.calculate()

    return complexity_factors


if __name__ == "__main__":
    try:
        parser = FaultTreeGeneratorArgParser()
        args, leftovers = parser.parse_known_args()
        factors = setup_factors(args)
        fault_tree = GenerativeFaultTree(args.ft_name, factors, args.root)
        print(str(fault_tree))
    except argparse.ArgumentTypeError as err:
        print("Argument Error:\n" + str(err))
        sys.exit(2)
    except ComplexityFactorError as err:
        print("Error in complexity factors:\n" + str(err))
        sys.exit(1)
