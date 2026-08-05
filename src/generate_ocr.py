import os
from dotenv import load_dotenv
import asyncio
from pypaperless import PaperlessClient
import structlog

from utils import patch_document
from llms import get_ocr_with_mistral

# Load environment variables from .env file
load_dotenv()

logger = structlog.get_logger(__name__)


async def ocr_document(document_id, remove_tag_id=None):
    """
    Asynchronously performs OCR (Optical Character Recognition) on a document and updates its content in Paperless.
    Args:
        document_id (int): The ID of the document to process.
        remove_tag_id (Optional[int]): The ID of a tag to remove from the document. If None, no tags are removed.
    Returns:
        None
    Steps:
        1. Initializes the Paperless connection.
        2. Retrieves document details and downloads its content.
        3. Performs OCR on the downloaded content using the `get_ocr_with_mistral` function.
        4. Updates the document's content in Paperless with the OCR result.
        5. Optionally removes a specified tag from the document.
        6. Closes the Paperless connection.
    Raises:
        Any exceptions raised during the Paperless API calls or OCR processing.
    """

    # Built per call: the client cannot be reused once closed, so a module-level
    # instance would fail with "Session is closed" on the second document of a
    # batch. The context manager initializes it and guarantees the close.
    async with PaperlessClient(os.getenv("PAPERLESS_BASE_URL"),
                               os.getenv("PAPERLESS_API_KEY")) as paperless:
        logger.info("Processing document", document_id=document_id)

        # Collect document information from paperless
        logger.info("Reading document details from paperless", document_id=document_id)
        document = await paperless.documents(document_id)
        download = await paperless.documents.download(document_id)

        ocr_text = get_ocr_with_mistral(download.content)
        logger.info("OCR text extracted", document_id=document_id, ocr_text_length=len(ocr_text))

        # Writing an empty result would overwrite the existing content with
        # nothing. Keep the tag so the document is retried and stays visible.
        if not ocr_text.strip():
            logger.error("OCR returned no text, keeping existing content", document_id=document_id)
            return

        # Update the document with the new content
        logger.info("Updating document content in paperless", document_id=document_id)
        if remove_tag_id is not None:
            tags = document.tags
            logger.info("Document tags", document_id=document_id, tags=tags)

            tags = [tag for tag in tags if tag != remove_tag_id]
            logger.info("Removing tag from document", document_id=document_id, tag_id=remove_tag_id)
            patch_document(document_id, tags=tags, content=ocr_text)
        else:
            patch_document(document_id, content=ocr_text)


async def main():
    # Example usage
    document_id = 259
    
    # Process the document with the specified ID
    await ocr_document(document_id)
    logger.info("Finished processing document")


if __name__ == "__main__":
    asyncio.run(main())