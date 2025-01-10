import argparse as ap
from XML_dumper import XMLDumper
from event_tree import EventTree
import sys
from fault_tree_generator import fault_tree_generator
from fault_tree_generator import FactorError
import csv

def generate_et(arguments):
    print("Generating event tree...")
    event_tree_name = arguments.get('event_tree_name')
    number_of_functional_events = arguments.get('number_of_functional_events')
    seed_for_fault_tree_generation = arguments.get('seed_for_fault_tree_generation')
    number_of_basic_events_for_first_fault_tree = arguments.get('number_of_basic_events_for_first_fault_tree')
    average_number_of_gate_arguments= arguments.get('average_number_of_gate_arguments')
    weights_for_and_gate= arguments.get('weights_for_and_gate')
    weights_for_or_gate= arguments.get('weights_for_or_gate')
    weights_for_koutofn = arguments.get('weights_for_koutofn')
    weights_for_not_gate= arguments.get('weights_for_not_gate')
    weights_for_xor_gate= arguments.get('weights_for_xor_gate')
    average_percentage_of_common_basic_events_per_gate= arguments.get('average_percentage_of_common_basic_events_per_gate')
    average_percentage_of_common_gates_per_gate= arguments.get('average_percentage_of_common_gates_per_gate')
    average_number_of_parents_for_common_basic_events= arguments.get('average_number_of_parents_for_common_basic_events')
    average_number_of_parents_for_common_basic_gates= arguments.get('average_number_of_parents_for_common_basic_gates')
    number_of_gates= arguments.get('number_of_gates')
    maximum_probability_for_basic_events= arguments.get('maximum_probability_for_basic_events')
    minimum_probability_for_basic_events= arguments.get('minimum_probability_for_basic_events')
    number_of_house_events= arguments.get('number_of_house_events')
    number_of_common_cause_failure_groups= arguments.get('number_of_common_cause_failure_groups')
    size_of_common_cause_failure_group= arguments.get('size_of_common_cause_failure_group')
    model_for_common__cause_failure= arguments.get('model_for_common0__cause_failure')
    output_file_path= arguments.get('output_file_path')

    functional_events = [f"FE{index + 1}" for index in range(number_of_functional_events)]
    print(functional_events)
    sequences= [f"S{index}" for index in range(1, 2 ** number_of_functional_events+1)]
    print(sequences)

    event_tree = EventTree(event_tree_name)
    event_tree.functional_events_id=functional_events
    event_tree.functional_events_name=functional_events
    event_tree.sequences=sequences
    a= event_tree.to_xml()
    open_psa_et_model_directory = output_file_path+'/event_tree_demo_'+str(number_of_functional_events) +'FE'+'.xml'
    initiating_event_name= f'INIT{number_of_functional_events}'
    fault_tree_name_list=[]
    fault_tree_logic_list=[]
    fault_tree_list =[]
    model_data_list =[]
    for functional_event in range(number_of_functional_events):

        argv = [
            '--ft-name',  'FT'+ str(functional_event + 1),
            '--root', 'TOP',
            '--seed', str(seed_for_fault_tree_generation),
            '-b', str(functional_event*50 + number_of_basic_events_for_first_fault_tree),
            '-a', str(average_number_of_gate_arguments),
            '--weights-g', str(weights_for_and_gate), str(weights_for_or_gate), str(weights_for_koutofn),str(weights_for_not_gate),str(weights_for_xor_gate),
            '--common-b', str(average_percentage_of_common_basic_events_per_gate),
            '--common-g', str(average_percentage_of_common_gates_per_gate),
            '--parents-b',str(average_number_of_parents_for_common_basic_events),
            '--parents-g',str(average_number_of_parents_for_common_basic_gates),
            '-g', str(number_of_gates),
            '--max-prob', str(maximum_probability_for_basic_events),
            '--min-prob', str(minimum_probability_for_basic_events),
            '--num-house', str(number_of_house_events),
            '--num-ccf', str(number_of_common_cause_failure_groups),
            '--ccf-size',str(size_of_common_cause_failure_group),
            '--ccf-model',str(model_for_common__cause_failure),
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
    print("Generating fault tree(s)...")
    try:
        return fault_tree_generator(argv)
    except ap.ArgumentTypeError as err:
        print('Argument Error: \n' + str(err))
        sys.exit(2)
    except FactorError as err:
        print('Factor Error: \n' + str(err))
        sys.exit(1)


def parse_arguments(config_path):
    print("Parsing arguments...")
    # Dictionary to store variables
    arguments = {}

    with open(config_path, mode='r') as file:
        csv_reader = csv.reader(file)
        # Iterate over each row in the CSV
        for row in csv_reader:
            # Create variable names and values dynamically
            param_name = row[0].replace("-", "_").replace("=", "_").replace(" ", "_").lower()
            value = row[1]
            try:
                # Convert to appropriate data type
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                # Keep as string if conversion fails
                pass
            arguments[param_name] = value

    return arguments

def main ():
    configuration_file_directory = './../configuration/config.csv'
    arguments = parse_arguments(configuration_file_directory)
    generate_et(arguments)
if __name__ == '__main__':
    main()