from dotenv import load_dotenv
import re
import base64
import os
from mistralai.client import Mistral
from openai import OpenAI
from pathlib import Path
import structlog


# Load environment variables from .env file
load_dotenv()

logger = structlog.get_logger(__name__)

openai_client = OpenAI()
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Reasoning effort levels defined by the Responses API. Which of these a given
# model actually accepts is model-dependent (gpt-5.6-luna rejects "minimal" and
# "max"), so this tuple only guards against typos - the API is the authority on
# what the configured model supports.
VALID_REASONING_EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh", "max")
DEFAULT_REASONING_EFFORT = "low"


def _get_reasoning_effort():
    """
    Reads the reasoning effort for the OpenAI Responses API from the environment.

    Falls back to DEFAULT_REASONING_EFFORT if OPENAI_REASONING_EFFORT is unset or
    is not a known effort level, so a typo degrades the title quality instead of
    failing every request with a 400. A level that is valid in general but
    unsupported by the configured model is still rejected by the API.

    Returns:
        str: One of VALID_REASONING_EFFORTS.
    """

    effort = os.getenv("OPENAI_REASONING_EFFORT", DEFAULT_REASONING_EFFORT).strip().lower()

    if effort not in VALID_REASONING_EFFORTS:
        logger.warning("Invalid reasoning effort, falling back",
                       configured=effort,
                       fallback=DEFAULT_REASONING_EFFORT,
                       valid=VALID_REASONING_EFFORTS)
        return DEFAULT_REASONING_EFFORT

    return effort


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

    with open(Path(__file__).parent.parent / "prompts" / "title.txt", "r", encoding="utf-8") as f:
        instructions = f.read()

    instructions = instructions.replace("{{OPENAI_LANGUAGE}}", os.getenv("OPENAI_LANGUAGE"))
    
    model = os.getenv("OPENAI_MODEL")
    effort = _get_reasoning_effort()
    logger.info("Requesting title from OpenAI", model=model, reasoning_effort=effort)

    response = openai_client.responses.create(
        model=model,
        instructions=instructions,
        input=text,
        reasoning={"effort": effort},
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
        except Exception as e:
            # Returning None here would send the literal string "None" as the
            # data URI payload, so fail loudly instead.
            logger.error("Error encoding PDF to base64", error=str(e))
            raise

    # Getting the base64 string
    base64_pdf = _encode_pdf(document)

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