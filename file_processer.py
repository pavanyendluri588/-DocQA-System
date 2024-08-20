import os
from logging_config import logger
from typing import Any
from utilities import config
from pdf_processing import process_pdf
from word_processing import process_word_text
from txt_processing import process_text

def process_all_files(data_folder: str, vector_db: Any, openai_client: Any, model_name: str, text_chunker: Any) -> None:
    """
    Processes all PDF, TXT, and Word files in the specified data folder.

    Args:
        data_folder (str): The path to the folder containing files.
        vector_db (Any): An instance of the vector database to which documents will be added.
        openai_client (Any): An instance of the OpenAI client to interact with the API.
        model_name (str): The name of the OpenAI model to use for generating summaries.
        text_chunker (Any): An instance of the text splitter to use for splitting text.
    """

    # Check if the data folder exists
    if not os.path.exists(data_folder):
        logger.error(f"The specified data folder does not exist: {data_folder}")
        print(f"Error: The specified data folder does not exist: {data_folder}")
        return

    # Create the output folder for extracted images
    extracted_images_foldername = config["settings"].get("image_directory_name", "extracted_images") or "extracted_images"
    output_folder = os.path.join(data_folder, extracted_images_foldername)
    os.makedirs(output_folder, exist_ok=True)

    files = os.listdir(data_folder)
    if not files:
        logger.warning("No files found in the specified data folder.")
        print("Warning: No files found in the specified data folder.")
        return

    # Iterate through all files in the data folder
    for filename in files:
        file_path = os.path.join(data_folder, filename)

        try:
            if filename.lower().endswith('.pdf'):
                logger.info(f"Processing PDF file: {filename}")
                print(f"Processing PDF file: {filename}")
                process_pdf(file_path, output_folder, vector_db, openai_client, model_name, text_chunker)
                logger.info(f"Processed PDF file: {filename}")
                print(f"Processed PDF file: {filename}")

            elif filename.lower().endswith('.txt'):
                logger.info(f"Processing TXT file: {filename}")
                print(f"Processing TXT file: {filename}")
                process_text(file_path, vector_db, text_chunker)
                logger.info(f"Processed TXT file: {filename}")
                print(f"Processed TXT file: {filename}")

            elif filename.lower().endswith('.docx'):
                logger.info(f"Processing Word file: {filename}")
                print(f"Processing Word file: {filename}")
                process_word_text(file_path, vector_db, text_chunker)
                logger.info(f"Processed Word file: {filename}")
                print(f"Processed Word file: {filename}")

            else:
                if config["settings"]["image_directory_name"] != filename:
                    logger.warning(f"Unsupported file type: {filename}")
                    print(f"Warning: Unsupported file type: {filename}")

        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            print(f"Error processing file {filename}: {e}")

    logger.info("All files have been processed.")
    print("All files have been processed.")