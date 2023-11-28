import argparse
import sys
import random
from multiprocessing import Manager
from argparse import ArgumentTypeError
from fault_tree_generator import ComplexityFactorError, GenerativeFaultTree
from fault_tree_generator import FaultTreeGeneratorArgParser, ComplexityFactors
import concurrent.futures


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


# Define a function to generate a single fault tree
def generate(index, args, factors, lock, file_path):
    try:
        # Create a new fault tree with a unique name
        ft_name = f"{args.ft_name}_{index}"
        fault_tree = GenerativeFaultTree(name=ft_name, factors=factors, top_gate_name=args.root, timeout=args.timeout)
        result = fault_tree.to_openfta()

        with lock:
            if file_path == "stdout":
                sys.stdout.write(result + '\n')
            else:
                with open(file_path, 'a') as f:
                    f.write(result + '\n')

    except TimeoutError as e:
        return f"Fault tree {index} generation timed out: {e}"
    except Exception as e:
        return f"Fault tree {index} generation failed with exception: {e}"


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
        manager = Manager()
        lock = manager.Lock()
        # Use ProcessPoolExecutor for parallel processing
        with concurrent.futures.ProcessPoolExecutor(max_workers=parsed_args.max_workers) as executor:
            # Submit tasks to the executor
            future_to_index = {
                executor.submit(generate, i + 1, parsed_args, factors, lock, parsed_args.out): i + 1
                for i in range(parsed_args.max_trees)
            }

            # Process the results as they are completed
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    future.result()
                except concurrent.futures.TimeoutError:
                    print(f"Fault tree {index} generation timed out after {parsed_args.timeout} seconds.", file=sys.stderr)
                except Exception as e:
                    print(f"Fault tree {index} generation failed with exception: {e}", file=sys.stderr)

    except ArgumentTypeError as err:
        print("Argument Error:\n" + str(err), file=sys.stderr)
        sys.exit(2)
    except ComplexityFactorError as err:
        print("Error in complexity factors:\n" + str(err), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
