from dotenv import load_dotenv
import re
import base64
import os
from mistralai import Mistral
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

openai_client = OpenAI()
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def get_title_with_openai(text):
    """
    Generates a title for the given text using OpenAI's language model.
    This function reads a set of instructions from a file located at 
    "prompts/title.txt" and uses the OpenAI API to generate a title 
    based on the provided text input.
    Args:
        text (str): The input text for which a title needs to be generated.
    Returns:
        str: The generated title as output from the OpenAI API.
    Raises:
        FileNotFoundError: If the "prompts/title.txt" file is not found.
        openai.error.OpenAIError: If there is an issue with the OpenAI API request.
    """

    with open(os.path.join(os.path.dirname(__file__), "prompts", "title.txt"), "r", encoding="utf-8") as f:
        instructions = f.read()

    instructions = instructions.replace("{{OPENAI_LANGUAGE}}", os.getenv("OPENAI_LANGUAGE"))
    
    response = openai_client.responses.create(
        model=os.getenv("OPENAI_MODEL"),
        instructions=instructions,
        input=text,
    )

    return response.output_text


def get_ocr_with_mistral(document: bytes):
    """
    Extracts text from a PDF document using the Mistral OCR API.

    This function encodes the provided PDF document into a base64 string,
    sends it to the Mistral OCR API for processing, and returns the extracted
    text. Markdown image references in the extracted text are removed.

    Args:
        document (bytes): The PDF document as a byte string.

    Returns:
        str: The extracted text from the document, with markdown images removed.

    Raises:
        KeyError: If the environment variable "MISTRAL_API_KEY" is not set.
        Exception: If there is an error during the base64 encoding or OCR processing.
    """

    def _encode_pdf(document: bytes):
        """Encode the pdf to base64."""
        try:
            return base64.b64encode(document).decode('utf-8')
        except Exception as e:  # Added general exception handling
            print(f"Error: {e}")
            return None

    # Getting the base64 string
    base64_pdf = _encode_pdf(document)

    api_key = os.environ["MISTRAL_API_KEY"]

    ocr_response = mistral_client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}" 
        }
    )

    text = "\n".join(page.markdown for page in ocr_response.pages)

    # remove markdown images from the text with a regex
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text).strip()

    return text