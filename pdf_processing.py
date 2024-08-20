

import pdfplumber
from logging_config import logger
from typing import Any,List,Tuple
from vector_database import text_db_insetter,image_db_insetter
from image_processing import encode_image_base64
import fitz
import os
from image_processing import image_summary_generator
from utilities import text_splitter,config

def extract_text_from_page(page_data: Any, pdf_name: str, page_no: int) -> str:
    """
    Extracts text from a specified page of a PDF.

    Args:
        page_data (Any): The page data object from which to extract text.
        pdf_name (str): The name of the PDF file being processed.
        page_no (int): The page number from which to extract text.

    Returns:
        str: The extracted text from the page.

    Raises:
        Exception: If text extraction fails for any reason.
    """
    logger.info(f"Extracting text from PDF: {pdf_name}, Page No: {page_no}")
    
    try:
        extracted_text = page_data.extract_text()
        if extracted_text is None:
            raise ValueError(f"No text could be extracted from page {page_no} of {pdf_name}.")
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {pdf_name}, Page No: {page_no}. Error: {e}")
        raise Exception(f"Failed to extract text from page {page_no} of {pdf_name}.") from e

    return extracted_text


def extract_images_from_page(page_data: Any, pdf_name: str, page_no: int) -> List[Any]:
    """
    Extracts images from a specified page of a PDF.

    Args:
        page_data (Any): The page data object from which to extract images.
        pdf_name (str): The name of the PDF file being processed.
        page_no (int): The page number from which to extract images.

    Returns:
        List[Any]: A list of extracted images from the page.

    Raises:
        Exception: If image extraction fails for any reason.
    """
    logger.info(f"Extracting images from PDF: {pdf_name}, Page No: {page_no}")
    
    try:
        images = page_data.get_images(full=True)
        if not images:
            logger.warning(f"No images found on page {page_no} of {pdf_name}.")
    except Exception as e:
        logger.error(f"Error extracting images from PDF: {pdf_name}, Page No: {page_no}. Error: {e}")
        raise Exception(f"Failed to extract images from page {page_no} of {pdf_name}.") from e

    return images


def PDF_text_processor(pdf_path: str, vector_db: Any, text_chunker: Any) -> None:
    """
    Extracts text from a PDF, splits it into smaller chunks, and inserts the chunks into a vector database.

    Args:
        pdf_path (str): The path to the PDF file.
        vector_db (Any): An instance of the vector database to which documents will be added.
        text_chunker (Any): An instance of the text splitter to use for splitting the text.

    Raises:
        ValueError: If the PDF path is empty or invalid.
        Exception: If there is an error while processing the PDF or adding documents to the vector database.
    """
    if not pdf_path:
        raise ValueError("PDF path cannot be empty.")

    logger.info(f"Processing PDF: '{pdf_path}'")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                extracted_text = extract_text_from_page(page_data=page, pdf_name=pdf_path, page_no=page_num)
                split_texts = text_splitter(text=extracted_text,text_chunker=text_chunker)
                text_db_insetter(vector_db=vector_db, texts=split_texts, pdf_name=pdf_path, page_no=page_num)
    except Exception as e:
        logger.error(f"Error processing PDF: '{pdf_path}'. Error: {e}")
        raise Exception(f"Failed to process PDF: '{pdf_path}'.") from e

def PDF_image_processor(pdf_path: str, output_folder: str, vector_db: Any, openai_client: Any, model_name: str, text_chunker: Any) -> None:
    """
    Processes images from a PDF file, generates summaries, and inserts them into a vector database.

    Args:
        pdf_path (str): The path to the PDF file.
        output_folder (str): The folder where extracted images will be saved.
        vector_db (Any): An instance of the vector database to which documents will be added.
        openai_client (Any): An instance of the OpenAI client to interact with the API.
        model_name (str): The name of the OpenAI model to use for generating summaries.
        text_chunker (Any): An instance of the text splitter to use for splitting text summaries.

    Raises:
        ValueError: If the PDF path is empty or invalid.
        Exception: If there is an error while processing the PDF or adding documents to the vector database.
    """
    if not pdf_path:
        raise ValueError("PDF path cannot be empty.")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    logger.info(f"Processing PDF for image summaries: '{pdf_path}'")

    try:
        document = fitz.open(pdf_path)
        for page_num in range(document.page_count):
            page = document[page_num]
            images = extract_images_from_page(page_data=page, pdf_name=os.path.basename(pdf_path), page_no=page_num+1)

            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"{output_folder}/{os.path.basename(pdf_path)}_page_{page_num + 1}_image_{img_index + 1}.{image_ext}"

                # Save the extracted image
                with open(image_filename, "wb") as image_file:
                    image_file.write(image_bytes)
                logger.info(f"Saved image: {image_filename}")

                # Encode the image to Base64
                encoded_image = encode_image_base64(image_filename)

                # Generate a summary for the image
                image_summary = image_summary_generator(encoded_image, model_name, openai_client)
                logger.info(f"Successfully generated summary for image: {image_filename}")

                # Apply the text splitter on the image summary
                split_summaries = text_splitter(image_summary,text_chunker )
                logger.info(f"Successfully split image summary into chunks for image: {image_filename}")

                # Insert the split image summaries into the vector database
                image_db_insetter(vector_db, split_summaries, image_filename, os.path.basename(pdf_path), page_no = page_num + 1 )
                logger.info(f"Successfully inserted image summary chunks into vector database for image: {image_filename}")

    except Exception as e:
        logger.error(f"Error processing PDF: '{pdf_path}'. Error: {e}")
        raise Exception(f"Failed to process PDF: '{pdf_path}'.") from e
def process_pdf(pdf_path: str, output_folder: str, vector_db: Any, openai_client: Any, model_name: str, text_chunker: Any) -> None:
    """
    Processes a single PDF file using the PDF_image_processor and PDF_text_processor.

    Args:
        pdf_path (str): The path to the PDF file.
        output_folder (str): The folder where extracted images will be saved.
        vector_db (Any): An instance of the vector database to which documents will be added.
        openai_client (Any): An instance of the OpenAI client to interact with the API.
        model_name (str): The name of the OpenAI model to use for generating summaries.
        text_chunker (Any): An instance of the text splitter to use for splitting text.
    """
    logger.info(f"Processing PDF file: {pdf_path}")
            
    try:
        PDF_text_processor(pdf_path, vector_db, text_chunker)
        PDF_image_processor(pdf_path, output_folder, vector_db, openai_client, model_name, text_chunker)
    except Exception as e:
        logger.error(f"Error processing PDF file '{pdf_path}': {e}")