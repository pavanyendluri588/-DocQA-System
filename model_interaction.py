from vector_database import retrieve_documents, create_retriever
from typing import Any, List, Tuple
from image_processing import encode_image_base64
from langchain.schema import Document
from utilities import config


def context_extractor(similar_docs: List[Document], MAX_IMAGES: int) -> Tuple[str, List[str], str, dict]:
    """
    Extracts context and image paths from a list of documents.

    Args:
        similar_docs (List[Document]): A list of Document objects containing metadata and content.
        MAX_IMAGES (int): The maximum number of images to encode.

    Returns:
        Tuple[str, List[str], str, dict]: A tuple containing:
            - context (str): Concatenated text content from all documents.
            - list_encoded_images (List[str]): List of Base64 encoded images.
            - model (str): The model name based on the presence of images.
            - references (dict): A dictionary mapping text and images to their sources.
    """

    list_image_paths = set()  # Use a set for O(1) lookups
    list_encoded_images = []
    context = ""
    
    # Retrieve the OpenAI model, defaulting to "gpt-3.5-turbo" if not set
    model_name = config["openai"].get("openai_only_text_model", "gpt-3.5-turbo") or "gpt-3.5-turbo"
    
    references = {
        "text": [],  # To store the first text reference
        "image": []  # To store the first image reference
    }

    first_text_reference_found = False
    first_image_reference_found = False

    for doc in similar_docs:
        try:
            doc_type = doc.metadata.get("Type")
            pdf_name = doc.metadata.get("Source")  # Assuming Source is a key in metadata
            page_no = doc.metadata.get("PageNo")    # Assuming PageNo is a key in metadata

            if doc_type == "Image" and len(list_encoded_images) < MAX_IMAGES:
                image_path = doc.metadata.get("ImagePath")
                if image_path not in list_image_paths:
                    encoded_image = encode_image_base64(image_path)
                    list_encoded_images.append(encoded_image)
                    list_image_paths.add(image_path)  # Track added image paths

                    if not first_image_reference_found:
                        references["image"].append({"pdf_name": pdf_name, "page_no": page_no})
                        first_image_reference_found = True

                    # Retrieve the OpenAI model, defaulting to "gpt-4o" if not set
                    model_name = config["openai"].get("openai_text_image_model", "gpt-4o") or "gpt-4o"

            elif doc_type == "Text":
                context += doc.page_content + "\n"
                if not first_text_reference_found:
                    references["text"].append({"pdf_name": pdf_name, "page_no": page_no})
                    first_text_reference_found = True

        except Exception as e:
            # Log the error or handle it as needed
            print(f"Error processing document: {e}")  # Replace with proper logging

    # Strip the context and ensure references are single entries
    return context.strip(), list_encoded_images, model_name, {
        "text": references["text"][:1],  # Only the first text reference
        "image": references["image"][:1]  # Only the first image reference, if available
    }


def structure_references(references: dict) -> str:
    """
    Structures the references from the given dictionary into a formatted string.

    Args:
        references (dict): A dictionary containing 'text' and 'image' references.

    Returns:
        str: A formatted string of references.
    """
    formatted_references = []

    if references.get("text"):
        formatted_references.append("Text:")
        for ref in references["text"]:
            pdf_name = ref.get("pdf_name", "Unknown Source").strip()
            page_no = ref.get("page_no", "Unknown Page")
            formatted_references.append(f"   PDF Name: {pdf_name}  Page No: {page_no}")

    if references.get("image"):
        if formatted_references:
            formatted_references.append("")
        formatted_references.append("Images:")
        for ref in references["image"]:
            pdf_name = ref.get("pdf_name", "Unknown Source").strip()
            page_no = ref.get("page_no", "Unknown Page")
            formatted_references.append(f"   PDF Name: {pdf_name}  Page No: {page_no}")

    return "\n".join(formatted_references)


def model_response(context: str, image_encodings: list, model_name: str, openai_client: Any, question: str) -> str:
    """
    Generates a model response based on the provided context, images, and question.

    Args:
        context (str): The reference context for answering the question.
        image_encodings (list): A list of Base64 encoded images.
        model_name (str): The name of the OpenAI model to use for generating the response.
        openai_client: The OpenAI client instance.
        question (str): The question to be answered.

    Returns:
        str: The generated model response as a string.
    """
    text_context = f"**Question:** {question} \n**Context:** {context}\n\n"

    if len(context) == 0 and len(image_encodings) == 0:
        return "Your question found no relevant answers from the document"

    if model_name == config["openai"]["openai_text_image_model"]:
        image_context = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_encoding}"}}
            for image_encoding in image_encodings
        ]

        response_from_model = openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content":"You are an advanced AI assistant designed to provide accurate, concise, and contextually relevant answers to user questions. Your responses should be clear, informative, and formatted in Markdown. Guidelines: Context Utilization: Use the provided context to answer the question at the end. Ensure your response is relevant and integrates the context effectively. Highlight key points from the context to support your answer. Response Clarity: Structure your answers to enhance readability. Use headings, bullet points, and lists where appropriate. Ensure that your language is straightforward and avoids jargon unless necessary. Honesty in Responses: If you do not know the answer to a question, clearly state that you do not know, without attempting to fabricate a response. Avoid guesswork and provide only verified information. Integration of Visuals: When images or additional context are provided, incorporate this information into your answers to enhance understanding. Reference visuals when necessary to clarify your points. User Engagement: Aim to engage users with a friendly and professional tone. Encourage follow-up questions or clarifications to ensure user satisfaction. Formatting Standards: Use appropriate Markdown formatting for headings, lists, and emphasis (bold/italics) to improve the presentation of your answers"
},
                {"role": "user", "content": [{"type": "text", "text": text_context}] + image_context}
            ],
            temperature=config["openai"]["temperature"],
        )

        return response_from_model.choices[0].message.content

    elif model_name == config["openai"]["openai_only_text_model"]:
        response_from_model = openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an advanced AI assistant designed to provide accurate, concise, and contextually relevant answers to user questions. Your responses should be clear, informative, and formatted in Markdown. Guidelines: Context Utilization: Use the provided context to answer the question at the end. Ensure your response is relevant and integrates the context effectively. Highlight key points from the context to support your answer. Response Clarity: Structure your answers to enhance readability. Use headings, bullet points, and lists where appropriate. Ensure that your language is straightforward and avoids jargon unless necessary. Honesty in Responses: If you do not know the answer to a question, clearly state that you do not know, without attempting to fabricate a response. Avoid guesswork and provide only verified information. Integration of Visuals: When images or additional context are provided, incorporate this information into your answers to enhance understanding. Reference visuals when necessary to clarify your points. User Engagement: Aim to engage users with a friendly and professional tone. Encourage follow-up questions or clarifications to ensure user satisfaction. Formatting Standards: Use appropriate Markdown formatting for headings, lists, and emphasis (bold/italics) to improve the presentation of your answers"},
                {"role": "user", "content": [{"type": "text", "text": text_context}]}
            ],
            temperature=config["openai"]["temperature"],
        )

        return response_from_model.choices[0].message.content

    else:
        raise ValueError(f"Invalid model name: {model_name}")


def generate_answer_from_vector_db(retriever, user_question: str, max_images: int, openai_client) -> Tuple[str, str]:
    """
    Generates an answer to a user question using the provided document retriever and OpenAI client.

    Args:
        retriever (Retriever): The retriever instance used to fetch relevant documents.
        user_question (str): The question posed by the user.
        max_images (int): The maximum number of images to include in the response.
        openai_client: The OpenAI client instance.

    Returns:
        Tuple[str, str]: A tuple containing the structured references and the generated response.
    """
    # Retrieve documents relevant to the user's question
    similar_documents = retrieve_documents(retriever, user_question)

    # Extract context, image encodings, model name, and references from the documents
    context, image_encodings, model_name, references = context_extractor(similar_documents, max_images)

    # Generate a response using the extracted context and images
    generated_response = model_response(
        context=context,
        image_encodings=image_encodings,
        question=user_question,
        model_name=model_name,
        openai_client=openai_client
    )

    # Structure the references into a formatted string
    formatted_references = structure_references(references)

    # Return the formatted references and the generated response as a tuple
    return formatted_references, generated_response
