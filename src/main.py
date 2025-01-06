import argparse as ap
from XML_dumper import XMLDumper
from event_tree import EventTree
import sys
import argparse
import fault_tree_generator
from fault_tree_generator import FactorError

def generate_et(number_of_functional_events):
    print("Generating event tree...")

def generate_ft(argv=None):
    print("Generating fault tree...")
    try:
        fault_tree = fault_tree_generator.fault_tree_generator()
    except ap.ArgumentTypeError as err:
        print('Argument Error: \n' + str(err))
        sys.exit(2)
    except FactorError as err:
        print('Factor Error: \n' + str(err))
        sys.exit(1)


def main ():

    #1.directories for generated models.
    open_psa_model_directory = './../models/open-psa/'
    saphsolve_model_directory = './../models/saphsolve/'
    ftrex_model_directory = './../models/ftrex/'

    #2.definition of number of functional events
    number_of_functional_events = input('Number of functional events: ')

    #3.generate pra model
    generate_et(number_of_functional_events)
    generate_ft()

if __name__ == '__main__':
    main()