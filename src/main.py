import argparse as ap
from XML_dumper import XMLDumper
from event_tree import EventTree
import sys
import argparse
from fault_tree_generator import fault_tree_generator
from fault_tree_generator import FactorError

def generate_et(number_of_functional_events):
    print("Generating event tree...")
    functional_events = [f"FE{index + 1}" for index in range(number_of_functional_events)]
    print(functional_events)
    sequences= [f"S{index}" for index in range(1, 2 ** number_of_functional_events+1)]
    print(sequences)
    event_tree_name='event-Tree'
    event_tree = EventTree(event_tree_name)
    event_tree.functional_events_id=functional_events
    event_tree.functional_events_name=functional_events
    event_tree.sequences=sequences
    a= event_tree.to_xml()
    open_psa_model_directory = './../models/open-psa/event_tree.xml'
    initiating_event_name= f'INIT{number_of_functional_events}'
    xml_dumper =XMLDumper(initiating_event_name, event_tree_name)
    xml_dumper.dump_object_to_xml(a,open_psa_model_directory)

def generate_ft(argv=None):
    print("Generating fault tree...")
    try:
        fault_tree =fault_tree_generator(argv)
    except ap.ArgumentTypeError as err:
        print('Argument Error: \n' + str(err))
        sys.exit(2)
    except FactorError as err:
        print('Factor Error: \n' + str(err))
        sys.exit(1)

def convert_to_xml():
    print("Dumping PRA model...")


def main ():

    #1.directories for generated models.
    open_psa_model_directory = './../models/open-psa/'
    saphsolve_model_directory = './../models/saphsolve/'
    ftrex_model_directory = './../models/ftrex/'

    #2.definition of number of functional events
    number_of_functional_events = int(input('Number of functional events: '))
    #3.generate pra model

    generate_et(number_of_functional_events)
    for functional_event in range(number_of_functional_events):

        argv = [
            '--ft-name',  'FT'+ str(functional_event + 1),
            '--root', 'TOP',
            '-b', str(functional_event + 100),
            '-o', str(open_psa_model_directory) + 'test' + str(functional_event + 1) + '.xml',
            ]
        print('Generated command line arguments: ', argv)

        generate_ft(argv)

    #4.dump pra mode
    convert_to_xml()

if __name__ == '__main__':
    main()