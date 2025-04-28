import argparse
import sys
import csv
import logging
from XML_dumper import XMLDumper
from event_tree import EventTree
from fault_tree_generator import fault_tree_generator, FactorError

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_arguments(config_path):
    """
    Parse the arguments from a CSV configuration file.

    Args:
        config_path (str): Path to the configuration CSV file.

    Returns:
        dict: Dictionary of arguments with parameter names as keys and values as corresponding values.
    """
    logging.info("Parsing arguments from CSV configuration file...")
    arguments = {}

    try:
        with open(config_path, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                param_name = row[0].replace("-", "_").replace("=", "_").replace(" ", "_").lower()
                value = row[1]

                # Attempt to convert value to appropriate type (int, float, or keep as string)
                value = convert_value(value)
                arguments[param_name] = value
    except FileNotFoundError:
        logging.error(f"Configuration file {config_path} not found.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error while parsing arguments: {str(e)}")
        sys.exit(1)

    return arguments


def convert_value(value):
    """
    Convert a string value to the appropriate data type.

    Args:
        value (str): The value to be converted.

    Returns:
        str, int, or float: Converted value.
    """
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        return value  # Keep the value as string if conversion fails


def generate_et(arguments):
    """
    Generate an event tree based on parsed arguments and store results in XML.

    Args:
        arguments (dict): Parsed arguments as a dictionary.
    """
    logging.info("Generating event tree...")

    # Extract necessary parameters from arguments
    functional_events = [f"FE{index + 1}" for index in range(arguments['number_of_functional_events'])]
    sequences = [f"S{index}" for index in range(1, 2 ** arguments['number_of_functional_events'] + 1)]

    event_tree = EventTree(arguments['event_tree_name'])
    event_tree.functional_events_id = functional_events
    event_tree.functional_events_name = functional_events
    event_tree.sequences = sequences

    # Generate event tree XML
    event_tree_xml = event_tree.to_xml()
    open_psa_et_model_directory = f"{arguments['output_file_path']}/event_tree_demo_{arguments['number_of_functional_events']}FE.xml"

    # Generate fault tree(s)
    fault_tree_name_list, fault_tree_logic_list, model_data_list = generate_fault_trees(arguments)

    # Create XML dumper and save the event tree and fault tree data to XML
    initiating_event_name = f"INIT{arguments['number_of_functional_events']}"
    xml_dumper = XMLDumper(initiating_event_name, arguments['event_tree_name'])
    xml_dumper.fault_tree_name_list = fault_tree_name_list
    xml_dumper.fault_tree_logic_list = fault_tree_logic_list
    xml_dumper.model_data_list = [model_data_list[-1]]  # Temporary approach for model data
    xml_dumper.dump_object_to_xml(event_tree_xml, open_psa_et_model_directory)


def generate_fault_trees(arguments):
    """
    Generate the fault tree(s) based on the provided arguments.

    Args:
        arguments (dict): Dictionary of configuration arguments.

    Returns:
        tuple: A tuple containing lists of fault tree names, fault tree logic, and model data.
    """
    fault_tree_name_list = []
    fault_tree_logic_list = []
    model_data_list = []

    for functional_event in range(arguments['number_of_functional_events']):
        argv = build_ft_arguments(functional_event, arguments)
        logging.debug(f"Generated fault tree arguments: {argv}")

        fault_tree_name_list.append(argv[1])
        fault_tree_logic_list.append(generate_ft(argv).replace('\n',''))

        # Split the result into model data and logic parts
        result = fault_tree_logic_list[-1]
        if 'model-data' in result:
            before, model_data = result.split('<model-data>', 1)
            model_data_list.append('<model-data>' + model_data)
            fault_tree_logic_list[-1] = before

    return fault_tree_name_list, fault_tree_logic_list, model_data_list


def build_ft_arguments(functional_event, arguments):
    """
    Build the arguments for generating the fault tree.

    Args:
        functional_event (int): Index of the functional event.
        arguments (dict): Dictionary of configuration arguments.

    Returns:
        list: List of arguments for generating the fault tree.
    """
    return [
        '--ft-name', f'FT{functional_event + 1}',
        '--root', 'TOP',
        '--seed', str(arguments['seed_for_fault_tree_generation']),
        '-b', str(functional_event * 50 + arguments['number_of_basic_events_for_first_fault_tree']),
        '-a', str(arguments['average_number_of_gate_arguments']),
        '--weights-g', str(arguments['weights_for_and_gate']),
        str(arguments['weights_for_or_gate']),
        str(arguments['weights_for_koutofn']),
        str(arguments['weights_for_not_gate']),
        str(arguments['weights_for_xor_gate']),
        '--common-b', str(arguments['average_percentage_of_common_basic_events_per_gate']),
        '--common-g', str(arguments['average_percentage_of_common_gates_per_gate']),
        '--parents-b', str(arguments['average_number_of_parents_for_common_basic_events']),
        '--parents-g', str(arguments['average_number_of_parents_for_common_basic_gates']),
        '-g', str(arguments['number_of_gates']),
        '--max-prob', str(arguments['maximum_probability_for_basic_events']),
        '--min-prob', str(arguments['minimum_probability_for_basic_events']),
        '--num-house', str(arguments['number_of_house_events']),
        '--num-ccf', str(arguments['number_of_common_cause_failure_groups']),
        '--ccf-size', str(arguments['size_of_common_cause_failure_group']),
        '--ccf-model', str(arguments['model_for_common_cause_failure']),
        '--event_tree_generator'
    ]


def generate_ft(argv):
    """
    Generate a fault tree using the provided arguments.

    Args:
        argv (list): List of arguments for generating the fault tree.

    Returns:
        str: The generated fault tree.
    """
    logging.info("Generating fault tree(s)...")
    try:
        return fault_tree_generator(argv)
    except argparse.ArgumentTypeError as err:
        logging.error(f"Argument error: {err}")
        sys.exit(2)
    except FactorError as err:
        logging.error(f"Factor error: {err}")
        sys.exit(1)


def main():
    """
    Main function to parse the configuration and generate the event tree and fault trees.
    """
    configuration_file_directory = './../configuration/config.csv'
    arguments = parse_arguments(configuration_file_directory)
    generate_et(arguments)


if __name__ == '__main__':
    main()