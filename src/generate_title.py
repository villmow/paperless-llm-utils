import os
from dotenv import load_dotenv
import asyncio
from pypaperless import Paperless

from utils import patch_document
from llms import get_ocr_with_mistral, get_title_with_openai


# Load environment variables from .env file
load_dotenv()

    
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

    print(f'Document ID {document_id}: Processing document')

    # Collect document information from paperless
    print(f'Document ID {document_id}: Reading document details from paperless.')
    document = await paperless.documents(document_id)

    if not document.content.strip():
        print(f'Document ID {document_id}: Document content is empty. Skipping title generation.')
        return
    
    # Get the title using OpenAI
    print(f'Document ID {document_id}: Generating title using OpenAI.')
    title = get_title_with_openai(document.content)

    print(f'Document ID {document_id}: Generated title: {title}')
    
    # Update the document with the new title
    print(f'Document ID {document_id}: Updating document title in paperless.')
    if remove_tag_id is not None:
            tags = document.tags
            print(f'Document ID {document_id}: Document tags: {tags}')

            tags = [tag for tag in tags if tag != remove_tag_id]
            print(f'Document ID {document_id}: Removing tag {remove_tag_id} from document.')
            patch_document(document_id, title=title, tags=tags)
    else:
        patch_document(document_id, title=title)

    await paperless.close()


async def main():
    async with paperless:

        # Example usage
        document_id = 261
        
        # Process the document with the specified ID
        await titelize_document(document_id, remove_tag_id=int(os.getenv("PAPERLESS_GENERATE_TITLE_TAG_ID")))

    print('Finished processing document.')


if __name__ == "__main__":
    asyncio.run(main())