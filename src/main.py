import asyncio
from dotenv import load_dotenv
import os

from generate_title import titelize_document
from generate_ocr import ocr_document

from utils import find_documents_with_tag_id, patch_document


# Load environment variables from .env file
load_dotenv()


async def run_for_tag(tag, func):
    if tag is None:
        print("No tag specified in the configuration.")
        return

    # Convert the tag to an integer
    try:
        tag = int(tag)
    except ValueError:
        print(f"Invalid tag ID: {tag}. Please provide a valid integer.")
        return
    
    # Find documents with the specified tag
    documents = find_documents_with_tag_id(tag)
    if documents:
        # Print the number of documents found with the tag
        print(f"Found: {len(documents)} documents with tag: {tag}")

        # Start editing the documents
        print('Begin editing the documents.')
        total_documents = len(documents)
        # Iterate through the documents
        for index, doc_id in enumerate(documents, start=1):
            print('#############################')
            # Print the current document being processed
            print(f'Start processing document {index} of {total_documents}.')
            await func(str(doc_id), remove_tag_id=tag)
    else:
        # If no documents are retrieved
        print("No documents retrieved.")


async def main():
    print('#############################')
    print('Begin OCRing documents.')
    await run_for_tag(os.getenv("PAPERLESS_GENERATE_OCR_TAG_ID", None), ocr_document)

    # Process the document with the specified ID
    print('#############################')
    print('Begin titelizing documents.')
    await run_for_tag(os.getenv("PAPERLESS_GENERATE_TITLE_TAG_ID", None), titelize_document)
    

if __name__ == "__main__":
    asyncio.run(main())