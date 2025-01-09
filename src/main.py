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
    open_psa_et_model_directory = './../models/open-psa/event_tree_demo_'+str(number_of_functional_events) +'FE'+'.xml'
    initiating_event_name= f'INIT{number_of_functional_events}'
    fault_tree_name_list=[]
    fault_tree_logic_list=[]
    fault_tree_list =[]
    model_data_list =[]
    for functional_event in range(number_of_functional_events):

        argv = [
            '--ft-name',  'FT'+ str(functional_event + 1),
            '--root', 'TOP',
            '-b', str(functional_event*50 + 100),
            '--event_tree_generator'
            ]
        print('Generated command line arguments: ', argv)

        fault_tree_name_list.append(argv[1])
        fault_tree_list.append(generate_ft(argv).replace('\n',''))
    for s in fault_tree_list:
        if 'model-data' in s:
            # Split into two parts: before and starting from <model-data>
            before, model_data = s.split('<model-data>',1)
            # Add <model-data> part to the model_data_list
            model_data_list.append('<model-data>' + model_data)
            # Add the part before <model-data> to the fault_tree_logic_list
            fault_tree_logic_list.append(before)
        else:
            # Add the string to the updated list if no <model-data> is present
            fault_tree_logic_list.append(s)
    print(f'Fault tree logic: ==={fault_tree_logic_list}')
    print(f'Model data: ==={model_data_list}')
    xml_dumper =XMLDumper(initiating_event_name, event_tree_name)
    xml_dumper.fault_tree_name_list=fault_tree_name_list
    xml_dumper.fault_tree_logic_list=fault_tree_logic_list
    xml_dumper.model_data_list=[model_data_list[-1]] #temp approach
    xml_dumper.dump_object_to_xml(a,open_psa_et_model_directory)

def generate_ft(argv=None):
    print("Generating fault tree...")
    try:
        return fault_tree_generator(argv)
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

    #4.dump pra mode
    convert_to_xml()

if __name__ == '__main__':
    main()