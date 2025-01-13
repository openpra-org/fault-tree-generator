import os
import csv
import logging
from lxml import etree

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("validation_process.log"),
        logging.StreamHandler()
    ]
)

def validate_xml(xml_file, relaxng):
    try:
        with open(xml_file, 'rb') as f:
            xml_doc = etree.parse(f)
        if relaxng.validate(xml_doc):
            return True, None
        else:
            return False, relaxng.error_log
    except etree.XMLSyntaxError as e:
        return False, [str(e)]

def main(xml_directory, schema_file, log_file):
    try:
        with open(schema_file, 'rb') as f:
            schema_root = etree.parse(f)
        relaxng = etree.RelaxNG(schema_root)
        logging.info("Successfully loaded and parsed the schema file.")
    except Exception as e:
        logging.error(f"Error parsing schema file: {e}")
        return

    try:
        with open(log_file, 'w', newline='') as csvfile:
            log_writer = csv.writer(csvfile)
            log_writer.writerow(['XML File', 'Status', 'Errors'])
            logging.info(f"Log file created: {log_file}")

            for root, _, files in os.walk(xml_directory):
                for file in files:
                    if file.endswith('.xml'):
                        xml_file = os.path.join(root, file)
                        valid, error_log = validate_xml(xml_file, relaxng)
                        if valid:
                            log_writer.writerow([xml_file, 'valid', ''])
                            logging.info(f"File {xml_file} is valid.")
                        else:
                            error_messages = "; ".join([str(error) for error in error_log])
                            log_writer.writerow([xml_file, 'invalid', error_messages])
                            logging.warning(f"File {xml_file} is invalid. Errors: {error_messages}")
        logging.info(f"Validation complete. Results are logged in {log_file}")
    except Exception as e:
        logging.error(f"An error occurred during validation: {e}")

if __name__ == "__main__":
    xml_directory = "./../models/open-psa/"
    schema_file = "./../schema/open-psa/schema_2.0.d/input.rng"
    log_file = "validation_log.csv"
    main(xml_directory, schema_file, log_file)