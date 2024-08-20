import base64
from typing import Any
import os
from utilities import config
from utilities import logger
def encode_image_base64(image_path: str) -> str:
    """
    Encodes an image file to a Base64 string.

    Args:
        image_path (str): The path to the image file to be encoded.

    Returns:
        str: The Base64 encoded string of the image.

    Raises:
        FileNotFoundError: If the image file does not exist.
        IOError: If there is an error reading the image file.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"The file '{image_path}' does not exist.")
    try:
        with open(image_path, 'rb') as image_file:
            image_filename = os.path.basename(image_path)
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            logger.info(f"Successfully encoded image: {image_filename}")
    except IOError as e:
        raise IOError(f"An error occurred while reading the image file: {e}")
    return encoded_image

def image_summary_generator(encoded_image: str, model_name: str, openai_client: Any) -> str:
    """
    Generates a summary of an image using a specified OpenAI model.

    Args:
        encoded_image (str): The Base64 encoded image string.
        model_name (str): The name of the OpenAI model to use for generating the summary.
        openai_client (Any): An instance of the OpenAI client to interact with the API.

    Returns:
        str: The generated summary of the image.

    Raises:
        ValueError: If the encoded image is empty or if the model response is invalid.
        Exception: If there is an error with the OpenAI API call.
    """
    if not encoded_image:
        raise ValueError("The encoded image string cannot be empty.")
    try:
        # Create the model response
        model_response = openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert image analyst. Your task is to analyze the provided image and generate a detailed summary.The summary should include key elements such as the main subjects, actions, context, and notable features of the image.This summary should be concise yet informative, making it suitable for retrieval when answering user questions related to the image."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Here is an image for you to summarize:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=config["openai"]["temperature"],
        )
        # Check if the model response is valid
        if not model_response.choices or not model_response.choices[0].message.content:
            raise ValueError("Invalid response from the model.")
        image_summary = model_response.choices[0].message.content
    except Exception as e:
        raise Exception(f"An error occurred while generating the image summary: {e}")
    return image_summary