from XML_dumper import XMLDumper
from event_tree import EventTree
import sys
import argparse
import fault_tree_generator
from fault_tree_generator import FactorError


def main ():

    #1.directories for generated models.
    open_psa_model_directory = './../models/open-psa/'
    saphsolve_model_directory = './../models/saphsolve/'
    ftrex_model_directory = './../models/ftrex/'

    fault_tree= fault_tree_generator.fault_tree_generator()

if __name__ == '__main__':
    main()