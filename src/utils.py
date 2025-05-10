import requests
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


def find_documents_with_tag_id(tag_id):
    paperless_base_url = os.getenv("PAPERLESS_BASE_URL")
    paperless_auth_header = {'Authorization': 'Token ' + os.getenv("PAPERLESS_API_KEY")}

    # Start URL
    documents_url = f"{paperless_base_url}/api/documents/?is_tagged=true&tags__id__all={tag_id}&fields=id"

    all_document_ids = []

    while documents_url:
        # Make a GET request to the Paperless API
        response = requests.get(documents_url, headers=paperless_auth_header)

        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            document_ids = [doc['id'] for doc in data['results']]
            all_document_ids.extend(document_ids)
            
            # Update the URL for the next page, if it exists
            documents_url = data.get('next', None)

        elif response.status_code == 404:
            print("No documents found for the specified tag.")
            return 
        else:
            print(f"Error: Received status code {response.status_code}")
            return 

    return all_document_ids


def patch_document(document_id, **kwargs):
    """
    Use this function to update a document field in Paperless. 
    
    pypaperless raises ServerErrors whysoever.
    """

    paperless_base_url = os.getenv("PAPERLESS_BASE_URL")
    paperless_auth_header = {'Authorization': 'Token ' + os.getenv("PAPERLESS_API_KEY")}

    patch_data = kwargs

    document_url = f"{paperless_base_url}/api/documents/{document_id}/"

    # Perform the PATCH request
    update_response = requests.patch(document_url, json=patch_data, headers=paperless_auth_header)

    # Check the result of the request
    if update_response.status_code == 200:
        print(f'Document ID {document_id}: Document updated successfully!')
        return True
    else:
        print(f'Document ID {document_id}: Error updating the document! Status code {update_response.status_code}')
        return False