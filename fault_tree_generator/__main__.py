import sys
import argparse

import fault_tree_generator
from fault_tree_generator import FactorError

if __name__ == "__main__":
    try:
        fault_tree_generator.main()
    except argparse.ArgumentTypeError as err:
        print("Argument Error:\n" + str(err))
        sys.exit(2)
    except FactorError as err:
        print("Error in factors:\n" + str(err))
        sys.exit(1)