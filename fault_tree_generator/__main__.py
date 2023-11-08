import argparse
import sys
import random
from argparse import ArgumentTypeError
from fault_tree_generator import ComplexityFactorError, GenerativeFaultTree
from fault_tree_generator import FaultTreeGeneratorArgParser, ComplexityFactors


def setup_factors(args: argparse.Namespace) -> ComplexityFactors:
    """Configures the fault generation by assigning factors based on parsed command-line arguments.

    This function initializes the ComplexityFactors object with the values provided from the command-line
    arguments. It sets up the probability boundaries, common event factors, size factors, gate weights,
    and calculates derived factors necessary for fault tree generation.

    Args:
        args: An argparse.Namespace object containing command-line arguments with values for factors.

    Returns:
        A fully initialized ComplexityFactors object.

    Raises:
        ArgumentTypeError: If there are problems with the command-line arguments.
        ComplexityFactorError: If there is an invalid setup for factors.
    """
    random.seed(args.seed)
    complexity_factors = ComplexityFactors()
    complexity_factors.set_min_max_prob(args.min_prob, args.max_prob)
    complexity_factors.set_common_event_factors(args.common_b, args.common_g, args.parents_b, args.parents_g)
    complexity_factors.set_num_factors(args.num_args, args.num_basic, args.num_house, args.num_ccf)
    complexity_factors.set_gate_weights([float(i) for i in args.weights_g])
    if args.num_gate:
        complexity_factors.constrain_num_gate(args.num_gate)
    complexity_factors.calculate()
    return complexity_factors


def main() -> None:
    """The main function for the fault tree generator script.

    This function parses command-line arguments, sets up complexity factors, generates a fault tree,
    and prints the fault tree to the standard output. If any errors occur during argument parsing or
    factor setup, the program will terminate with an appropriate error message and exit code.

    Raises:
        SystemExit: If an error occurs during argument parsing or factor setup.
    """
    try:
        parser = FaultTreeGeneratorArgParser()
        parsed_args, leftovers = parser.parse_known_args()
        factors = setup_factors(parsed_args)
        fault_tree = GenerativeFaultTree(parsed_args.ft_name, factors, parsed_args.root)
        print(fault_tree.expr())
    except ArgumentTypeError as err:
        print("Argument Error:\n" + str(err), file=sys.stderr)
        sys.exit(2)
    except ComplexityFactorError as err:
        print("Error in complexity factors:\n" + str(err), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
