import os
from dotenv import load_dotenv
import asyncio
from pypaperless import Paperless

from utils import patch_document
from llms import get_ocr_with_mistral, get_title_with_openai

# Load environment variables from .env file
load_dotenv()

paperless = Paperless(os.getenv("PAPERLESS_BASE_URL"), 
                      os.getenv("PAPERLESS_API_KEY"))

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
    
    await paperless.initialize()

    print(f'Document ID {document_id}: Processing document')

    # Collect document information from paperless
    print(f'Document ID {document_id}: Reading document details from paperless.')
    document = await paperless.documents(document_id)
    download = await document.get_download()
    
    ocr_text = get_ocr_with_mistral(download.content)
    print(f'Document ID {document_id}: OCR text: {ocr_text}')

    # Update the document with the new content
    print(f'Document ID {document_id}: Updating document content in paperless.')
    if remove_tag_id is not None:
            tags = document.tags
            print(f'Document ID {document_id}: Document tags: {tags}')

            tags = [tag for tag in tags if tag != remove_tag_id]
            print(f'Document ID {document_id}: Removing tag {remove_tag_id} from document.')
            patch_document(document_id, tags=tags, content=ocr_text)
    else:
        patch_document(document_id, content=ocr_text)

    await paperless.close()


async def main():
    # Example usage
    document_id = 259
    
    # Process the document with the specified ID
    await ocr_document(document_id)
    print('Finished processing document.')


if __name__ == "__main__":
    asyncio.run(main())