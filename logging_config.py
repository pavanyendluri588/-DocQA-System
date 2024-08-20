import logging
import json
import os
from logging.handlers import RotatingFileHandler

# Load logging configuration from JSON file
def load_logging_config(config_file='config.json'):
    """
    Loads the logging configuration from a specified JSON file.

    Args:
        config_file (str): The path to the JSON configuration file. 
                           Defaults to 'config.json'.

    Returns:
        dict: A dictionary containing the logging configuration. 
              Only the 'logging' section from the JSON file is returned.

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        json.JSONDecodeError: If the configuration file is not a valid JSON.
    """
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config['logging']  # Return only the logging section

# Configure logging
logging_config = load_logging_config()

log_file = os.getenv('LOG_FILE', logging_config['log_file'])
log_level = os.getenv('LOG_LEVEL', logging_config['log_level']).upper()
max_bytes = logging_config['max_bytes']
backup_count = logging_config['backup_count']
log_format = logging_config['format']

# Create a rotating file handler
handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
handler.setLevel(log_level)

# Create a formatter and set it for the handler
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)

# Create a logger object
logger = logging.getLogger(__name__)
logger.setLevel(log_level)
logger.addHandler(handler)

# Example usage
if __name__ == "__main__":
    logger.info("Logging system initialized.")