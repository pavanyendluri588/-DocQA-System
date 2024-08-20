from langchain.schema import Document
from typing import Any, List
import os
from logging_config import logger
from utilities import config

def image_db_insetter(vector_db: Any, image_summaries_texts: List[str], image_path: str, pdf_name: str, page_no: int) -> None:
    """
    Inserts image summary documents into a vector database.

    Args:
        vector_db (Any): An instance of the vector database to which documents will be added.
        image_summaries_texts (List[str]): A list of summary texts for the images to be added as documents.
        image_path (str): The file path of the image being processed.
        pdf_name (str): The name of the PDF source for the documents.
        page_no (int): The page number from which the image summaries were extracted.

    Raises:
        ValueError: If the image summaries list is empty or if the page number is invalid.
        Exception: If there is an error while adding documents to the vector database.
    """
    if not image_summaries_texts:
        raise ValueError("The image summaries list cannot be empty.")
    if page_no < 1:
        raise ValueError("Page number must be a positive integer.")
    
    documents = []
    for text in image_summaries_texts:
        documents.append(Document(page_content=text, metadata={
            "Source": os.path.basename(pdf_name),
            "PageNo": page_no,
            "ImagePath": image_path,
            "Type": "Image"
        }))
    
    try:
        vector_db.add_documents(documents=documents)
    except Exception as e:
        raise Exception(f"An error occurred while adding documents to the vector database: {e}")

def text_db_insetter(vector_db: Any, texts: List[str], pdf_name: str, page_no: int) -> None:
    """
    Inserts text documents into a vector database.

    Args:
        vector_db (Any): An instance of the vector database to which documents will be added.
        texts (List[str]): A list of text strings to be added as documents.
        pdf_name (str): The name of the PDF source for the documents.
        page_no (int): The page number from which the texts were extracted.

    Raises:
        ValueError: If the texts list is empty or if the page number is invalid.
        Exception: If there is an error while adding documents to the vector database.
    """
    if not texts:
        raise ValueError("The texts list cannot be empty.")
    if page_no < 1:
        raise ValueError("Page number must be a positive integer.")
    
    documents = []
    for text in texts:
        documents.append(Document(page_content=text, metadata={
            "Source": os.path.basename(pdf_name),
            "PageNo": page_no,
            "Type": "Text"
        }))
    
    try:
        vector_db.add_documents(documents=documents)
    except Exception as e:
        raise Exception(f"An error occurred while adding documents to the vector database: {e}")

def create_retriever(vector_db: Any, search_type: str, top_k: int) -> Any:
    """
    Create a retriever from a vector database with the specified search type and top-k results.

    Args:
        vector_db (Any): The vector database to create the retriever from.
        search_type (str): The type of search to use for the retriever.
        top_k (int): The number of top results to retrieve.

    Returns:
        Any: The created retriever.
    """
    retriever = vector_db.as_retriever(search_type=search_type, search_kwargs={"k": top_k})
    return retriever

def retrieve_documents(retriever: Any, question: str) -> List[Document]:
    """
    Retrieve documents based on a given question using the specified retriever.

    Args:
        retriever (Any): The retriever instance used to fetch documents.
        question (str): The question or query for which to retrieve documents.

    Returns:
        List[Document]: A list of documents retrieved based on the question.

    Raises:
        ValueError: If the question is empty or invalid.
        Exception: For any other errors during the retrieval process.
    """
    # Input validation
    if not question or not isinstance(question, str):
        logger.error("Invalid question provided: %s", question)
        raise ValueError("The question must be a non-empty string.")
    
    try:
        results = retriever.invoke(input=question)
        logger.info("Retrieved %d documents for question: %s", len(results), question)
        
        return results
    except Exception as e:
        logger.error("Error retrieving documents: %s", str(e))
        return []
