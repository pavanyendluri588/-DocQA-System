import os
from typing import Collection
import pandas as pd
from openai import OpenAI
import logging
from logging.handlers import RotatingFileHandler
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from vector_database import create_retriever
from model_interaction import generate_answer_from_vector_db
from logging_config import logger
from utilities import config
from file_processer import process_all_files
from dotenv import load_dotenv

load_dotenv()

def initialize_openai_client():
    """
    Initialize the OpenAI client.

    Returns:
        openai: Initialized OpenAI client.
    """
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return client

def initialize_vector_db(embedding_model_name, db_collection_name, vector_db_persist_directory):
    """
    Initialize the vector database.

    Args:
        embedding_model_name (str): Name of the embedding model.
        db_collection_name (str): Name of the database collection.
        vector_db_persist_directory (str): Directory to persist the vector database.

    Returns:
        Chroma: Initialized vector database.
    """
    embedding_function = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"), model=embedding_model_name)
    vector_db = Chroma(
        collection_name=db_collection_name,
        embedding_function=embedding_function,
        persist_directory=vector_db_persist_directory
    )
    return vector_db

def log_to_excel(data, output_folder,output_excel_file_name):
    """
    Log the question, response, and references to an Excel file.

    Args:
        data (list): List of dictionaries containing question, response, and references.
        output_folder (str) : Contains the name of the output folder.
        output_excel_file_name (str): Name of the output Excel file.
    """
    if not data:
        logger.warning("No data to log.")
        return
    # Convert data to a DataFrame
    df = pd.DataFrame(data)
    try:
        #creating the output folder is not exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        excelfile_full_path = os.path.join(output_folder,output_excel_file_name)
        # Check if the output file already exists
        if os.path.exists(excelfile_full_path):
            # Append dasta to existing Excel file
            with pd.ExcelWriter(excelfile_full_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                # Determine the starting row for appending
                start_row = writer.sheets['Sheet1'].max_row
                df.to_excel(writer, index=False, header=False, startrow=start_row)
                logger.info(f"Appended data to {output_excel_file_name}.")
                print(f"Appended results to {output_excel_file_name}.")
        else:
            # Create a new Excel file and save data
            with pd.ExcelWriter(excelfile_full_path, mode='w', engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
                logger.info(f"Created new file and saved results to {output_excel_file_name}.")
                print(f"Created new file and saved results to {output_excel_file_name}.")
    except Exception as e:
        logger.error(f"Error logging data to Excel: {e}")

def ask_question(retriever, openai_client, max_images, output_folder,output_excel_file_name):
    """
    Prompt user for questions and log responses.

    Args:
        retriever (object): Retriever instance for generating answers.
        openai_client (openai): Initialized OpenAI client.
        max_images (int): Maximum number of images to generate.
        output_folder (str) : Contains the name of the output folder.
        output_excel_file_name (str): Name of the output Excel file.
    """
    log_data = []
    while True:
        question = input("Enter Question (or 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        try:
            references, response = generate_answer_from_vector_db(retriever, user_question=question, max_images=max_images, openai_client=openai_client)
            print(f"References:\n{references}\nResponse:\n{response}")
            # Log the question, response, and references
            log_data.append({
                'Question': question,
                'Response': response,
                'References': references
            })
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            continue
        # Save the logged data to Excel after each question
        log_to_excel(log_data, output_folder,output_excel_file_name)
        log_data = []  # Reset the log_data list

def main():
    """
    Main function to run the application.
    """
    # Load constants from config
    data_folder = config['settings']['input_folder']
    multimodel_model_name = config['openai']["openai_text_image_model"]
    embedding_model_name = config['VectorDB']['embedding_model_name']
    db_collection_name = config['VectorDB']["collection_name"]
    output_folder = config['settings']['output_folder']
    output_excel_file_name = config['settings']["output_excel_filename"]
    vector_db_persist_directory = config['VectorDB']['vector_db_persist_directory_name']
    retriever_search_algorithm_name = config['VectorDB']["retriever"]["search_algorithm"]
    retriver_max_images = config['VectorDB']["retriever"]["max_images"]
    retriver_top_k = config['VectorDB']["retriever"]["top_k"]

    openai_client = initialize_openai_client()

    vector_db = initialize_vector_db(
        db_collection_name=db_collection_name,
        embedding_model_name=embedding_model_name,
        vector_db_persist_directory=vector_db_persist_directory
    )

    # Initialize the text splitter
    text_chunker = RecursiveCharacterTextSplitter(
        chunk_size=config["text_splitter"]["chunk_size"],
        chunk_overlap=config["text_splitter"]["chunk_overlap"],
        length_function=len,
        is_separator_regex=False
    )

    # Create retriever instance
    retriever = create_retriever(vector_db, search_type=retriever_search_algorithm_name, top_k=retriver_top_k)

    # Process all PDFs in the specified folder
    try:
        process_all_files(data_folder, vector_db, openai_client, multimodel_model_name, text_chunker=text_chunker)
        
    except Exception as e:
        logger.error(f"Error processing files: {e}")

    # Start asking questions
    ask_question(retriever=retriever, openai_client=openai_client, max_images=retriver_max_images,output_folder =output_folder , output_excel_file_name=output_excel_file_name)

if __name__ == "__main__":
    main()