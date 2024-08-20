import os
from typing import Any
from logging_config import logger
from vector_database import text_db_insetter
from utilities import text_splitter

def text_extracter(file_path: str) -> str:
    """Extracts and cleans text from a text file.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: Cleaned text extracted from the file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: If there is an error reading the file.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The specified file does not exist: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Remove unwanted newline characters
        cleaned_content = content.replace('\n', ' ')
        
        return cleaned_content
    except Exception as e:
        logger.error(f"Error reading file: '{file_path}'. Error: {e}")
        raise Exception(f"Failed to extract text from file: '{file_path}'.") from e

def process_text(file_path: str, vector_db: Any, text_chunker: Any) -> None:
    """Processes a text file by extracting text, chunking it, and inserting it into a vector database.

    Args:
        file_path (str): The path to the text file.
        vector_db (Any): An instance of the vector database to which documents will be added.
        text_chunker (Any): An instance of the text splitter to use for splitting the text.

    Raises:
        ValueError: If the file path is empty or invalid.
        Exception: If there is an error processing the file or adding documents to the vector database.
    """
    if not file_path:
        raise ValueError("File path cannot be empty.")

    logger.info(f"Processing file: '{file_path}'")

    try:
        # Extract text from the file
        extracted_text = text_extracter(file_path)

        split_texts = text_splitter(text=extracted_text,text_chunker=text_chunker)

        # Extract the file name from the path
        file_name = os.path.basename(file_path)

        text_db_insetter(vector_db=vector_db, texts=split_texts, pdf_name=file_name, page_no=1)

        logger.info(f"Successfully processed and inserted chunks from '{file_name}' into the vector database.")

    except ValueError as ve:
        logger.error(f"Value error while processing file: '{file_name}'. Error: {ve}")
    except Exception as e:
        logger.error(f"Error processing file: '{file_name}'. Error: {e}")
        raise Exception(f"Failed to process file: '{file_name}'.") from e