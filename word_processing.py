import os
from typing import Any
from langchain_community.document_loaders import Docx2txtLoader
from logging_config import logger
from vector_database import text_db_insetter
from utilities import text_splitter

def word_text_extracter(file_path: str) -> str:
    """Extracts and cleans text from a Word document.

    Args:
        file_path (str): The path to the Word document.

    Returns:
        str: Cleaned text extracted from the document.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: If there is an error loading the document.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The specified file does not exist: {file_path}")

    try:
        loader = Docx2txtLoader(file_path)
        data = loader.load()
        
        # Extract the page content
        page_content = data[0].page_content
        
        # Remove unwanted newline characters
        cleaned_content = page_content.replace('\n', ' ')
        
        return cleaned_content
    except Exception as e:
        logger.error(f"Error loading document: '{file_path}'. Error: {e}")
        raise Exception(f"Failed to extract text from Word document: '{file_path}'.") from e

def process_word_text(word_path: str, vector_db: Any, text_chunker: Any) -> None:
    """Processes a Word document by extracting text, chunking it, and inserting it into a vector database.

    Args:
        word_path (str): The path to the Word document.
        vector_db (Any): An instance of the vector database to which documents will be added.
        text_chunker (Any): An instance of the text splitter to use for splitting the text.

    Raises:
        ValueError: If the Word path is empty or invalid.
        Exception: If there is an error processing the Word document or adding documents to the vector database.
    """
    if not word_path:
        raise ValueError("Word path cannot be empty.")

    logger.info(f"Processing Word document: '{word_path}'")

    try:
        # Extract text from the Word document
        extracted_text = word_text_extracter(word_path)

        split_texts = text_splitter(text=extracted_text,text_chunker=text_chunker)

        # Extract the file name from the path
        file_name = os.path.basename(word_path)

        text_db_insetter(vector_db=vector_db, texts=split_texts, pdf_name=file_name, page_no=1)
        logger.info(f"Successfully processed and inserted chunks from '{file_name}' into the vector database.")

    except ValueError as ve:
        logger.error(f"Value error while processing Word document: '{word_path}'. Error: {ve}")
        raise
    except Exception as e:
        logger.error(f"Error processing Word document: '{word_path}'. Error: {e}")
        raise Exception(f"Failed to process Word document: '{word_path}'.") from e