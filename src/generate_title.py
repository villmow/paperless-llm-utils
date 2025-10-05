import os
from dotenv import load_dotenv
import asyncio
from pypaperless import Paperless
import structlog

from utils import patch_document
from llms import get_ocr_with_mistral, get_title_with_openai
import logging_config  # Initialize logging configuration


# Load environment variables from .env file
load_dotenv()

logger = structlog.get_logger(__name__)

    
async def titelize_document(document_id, remove_tag_id=None):
    """
    Asynchronously generates a title for a document using OpenAI and updates the document in Paperless.
    Args:
        document_id (int): The ID of the document to process.
        remove_tag_id (Optional[int]): The ID of a tag to remove from the document's tags. Defaults to None.
    Returns:
        None
    Behavior:
        - Initializes a connection to the Paperless API using environment variables for the base URL and API key.
        - Fetches the document details from Paperless using the provided document ID.
        - Skips processing if the document content is empty.
        - Generates a title for the document using OpenAI based on its content.
        - Updates the document's title in Paperless.
        - Optionally removes a specified tag from the document's tags if `remove_tag_id` is provided.
        - Closes the connection to the Paperless API after processing.
    Raises:
        Any exceptions raised by the Paperless API or OpenAI integration will propagate to the caller.
    """
    paperless = Paperless(os.getenv("PAPERLESS_BASE_URL"),
                        os.getenv("PAPERLESS_API_KEY"))

    await paperless.initialize()

    try:
        logger.info("Processing document", document_id=document_id)

        # Collect document information from paperless
        logger.info("Reading document details from paperless", document_id=document_id)
        document = await paperless.documents(document_id)

        if not document.content.strip():
            logger.warning("Document content is empty, skipping title generation", document_id=document_id)
            return

        # Get the title using OpenAI
        logger.info("Generating title using OpenAI", document_id=document_id)
        title = get_title_with_openai(document.content)

        logger.info("Generated title", document_id=document_id, title=title)

        # Update the document with the new title
        logger.info("Updating document title in paperless", document_id=document_id)
        if remove_tag_id is not None:
                tags = document.tags
                logger.info("Document tags", document_id=document_id, tags=tags)

                tags = [tag for tag in tags if tag != remove_tag_id]
                logger.info("Removing tag from document", document_id=document_id, tag_id=remove_tag_id)
                patch_document(document_id, title=title, tags=tags)
        else:
            patch_document(document_id, title=title)
    finally:
        await paperless.close()


async def main():
    async with paperless:

        # Example usage
        document_id = 261
        
        # Process the document with the specified ID
        await titelize_document(document_id, remove_tag_id=int(os.getenv("PAPERLESS_GENERATE_TITLE_TAG_ID")))

    logger.info("Finished processing document")


if __name__ == "__main__":
    asyncio.run(main())