from typing import Any, List
import json
from logging_config import logger

def text_splitter(text: str, text_chunker: Any) -> List[str]:
    """
    Splits a given text into smaller chunks using a text splitter.

    Args:
        text (str): The text to be split.
        text_chunker (Any): An instance of the text splitter to use for splitting the text.

    Returns:
        List[str]: A list of split text chunks.

    Raises:
        ValueError: If the input text is empty.
        Exception: If there is an error while splitting the text.
    """
    if not text:
        raise ValueError("The input text cannot be empty.")
    try:
        splited_text = text_chunker.split_text(text)
    except Exception as e:
        raise Exception(f"An error occurred while splitting the text: {e}")
    return splited_text

def load_config(config_path='config.json'):
    """
    Load configuration settings from a JSON file.

    Args:
        config_path (str): Path to the configuration file. Defaults to 'config.json'.

    Returns:
        dict or None: Configuration settings if successful, otherwise None.
    """
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logger.error(f"Config file '{config_path}' not found.")
        return None
    except json.JSONDecodeError:
        logger.error("Error decoding JSON config file.")
        return None
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return None

config = load_config()