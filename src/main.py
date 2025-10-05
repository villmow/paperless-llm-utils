import asyncio
from dotenv import load_dotenv
import os
import structlog

import logging_config  # noqa: F401 - Side effect: configures structlog

from generate_title import titelize_document
from generate_ocr import ocr_document

from utils import find_documents_with_tag_id


# Load environment variables from .env file
load_dotenv()

logger = structlog.get_logger(__name__)


async def run_for_tag(tag, func):
    if tag is None:
        logger.warning("No tag specified in the configuration")
        return

    # Convert the tag to an integer
    try:
        tag = int(tag)
    except ValueError:
        logger.error("Invalid tag ID provided", tag_id=tag)
        return

    # Find documents with the specified tag
    documents = find_documents_with_tag_id(tag)
    if documents:
        # Print the number of documents found with the tag
        logger.info("Found documents with tag", count=len(documents), tag_id=tag)

        # Start editing the documents
        logger.info("Begin editing documents")
        total_documents = len(documents)
        # Iterate through the documents
        for index, doc_id in enumerate(documents, start=1):
            # Print the current document being processed
            logger.info("Start processing document",
                       current=index,
                       total=total_documents,
                       document_id=doc_id)
            await func(str(doc_id), remove_tag_id=tag)
    else:
        # If no documents are retrieved
        logger.warning("No documents retrieved")


async def main():
    logger.info("Begin OCRing documents")
    await run_for_tag(os.getenv("PAPERLESS_GENERATE_OCR_TAG_ID", None), ocr_document)

    # Process the document with the specified ID
    logger.info("Begin titelizing documents")
    await run_for_tag(os.getenv("PAPERLESS_GENERATE_TITLE_TAG_ID", None), titelize_document)
    

if __name__ == "__main__":
    asyncio.run(main())