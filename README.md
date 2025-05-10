# Paperless-ngx LLM Utils

`paperless-llm-utils` is a lightweight script designed to enhance the functionality of [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx) with LLMs and OCR. The docker image automatically processes documents with specific tags from Paperless-ngx. It generates a title with ChatGPT or can be used to redo OCR text extraction with Mistral into a markdown format.

It is losely inspired and based on [paperless-ngx-openai-title](https://github.com/cgiesche/paperless-ngx-openai-title/tree/master).

## Features

- **Title Generation**: Uses OpenAI's models to generate meaningful titles for documents based on their OCR content.
- **OCR Text Extraction**: Extracts text from PDF documents using the Mistral OCR API.
- **Tag-Based Automation**: Processes documents in Paperless-ngx based on specific tags and removes the tags after processing to avoid duplication.

## How It Works

1. The script checks for documents in Paperless-ngx with specific tags:
   - `PAPERLESS_GENERATE_TITLE_TAG_ID`: For title generation.
   - `PAPERLESS_GENERATE_OCR_TAG_ID`: For OCR text extraction.
2. For each document with a tag:
   - It performs the corresponding task (title generation or OCR).
   - Removes the tag from the document after processing.
3. The script runs periodically (e.g., every 5 minutes) to check for new documents.
4. It can be run manually or deployed as a Docker container.

## Setup

### Prerequisites

- A running instance of [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx).
- API keys for:
  - OpenAI (for title generation)
  - Mistral (for OCR processing)
  - Paperless-ngx (for accessing the API)
- Python 3.12 or Docker (for deployment).

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/villmow/paperless-llm-utils.git
   cd paperless-llm-utils
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy the `example.env` file to `.env`:
     ```bash
     cp example.env .env
     ```
   - Fill in the required values in the `.env` file:
     - OpenAI API key
     - Mistral API key
     - Paperless-ngx API key and base URL
     - Tag IDs for title generation and OCR processing

4. Run the script:
   ```bash
   python src/main.py
   ```

## Deployment

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t paperless-llm-utils .
   ```

2. Run the container:
   ```bash
   docker run --env-file .env paperless-llm-utils
   ```

3. (Optional) Use Docker Compose for periodic execution:
   - Add a `docker-compose.yml` file with the following content:
     ```yaml
     services:
       paperless-llm-utils:
         build: .
         env_file: .env
         restart: always
         image: paperless-llm-utils
         container_name: paperless-llm-utils
     ```
   - Start the service:
     ```bash
     docker-compose up -d
     ```

### Using Cron (for periodic execution)

1. Add a cron job to execute the script periodically:
   ```bash
   crontab -e
   ```
2. Add the following line to run the script every 5 minutes:
   ```bash
   */5 * * * * python /path/to/src/main.py
   ```

## Development

### Adding New Functions for New Tags

To add support for new tags, follow these steps:

1. **Create a New Function**:
   - Add a new function in the appropriate module (e.g., `src/generate_<task>.py`).
   - The function should accept a `doc_id` and `remove_tag_id` as arguments and perform the desired task.

2. **Update `main.py`**:
   - Import the new function in `main.py`.
   - Add a new call to `run_for_tag` in the `main()` function:
     ```python
     await run_for_tag(os.getenv("PAPERLESS_GENERATE_<TASK>_TAG_ID", None), <new_function>)
     ```

3. **Add a New Environment Variable**:
   - Add a new tag ID in the `.env` file:
     ```env
     PAPERLESS_GENERATE_<TASK>_TAG_ID=<tag_id>
     ```

4. **Test the Functionality**:
   - Run the script and verify that documents with the new tag are processed correctly.

### Example: Adding a "Summarize Document" Task

1. Create a new file `src/generate_summary.py`:
   ```python
   async def summarize_document(doc_id, remove_tag_id):
       # Logic to summarize the document
       print(f"Summarizing document {doc_id}")
       # Remove the tag after processing
       patch_document(doc_id, remove_tag_id)
   ```

2. Update `main.py`:
   ```python
   from generate_summary import summarize_document

   async def main():
       ...
       await run_for_tag(os.getenv("PAPERLESS_GENERATE_SUMMARY_TAG_ID", None), summarize_document)
   ```

3. Add the new tag ID to `.env`:
   ```env
   PAPERLESS_GENERATE_SUMMARY_TAG_ID=19
   ```

4. Test the script:
   ```bash
   python src/main.py
   ```

## Environment Variables

The following environment variables must be configured in the `.env` file:

| Variable                        | Description                                                                 |
|---------------------------------|-----------------------------------------------------------------------------|
| `OPENAI_API_KEY`                | API key for OpenAI                                                         |
| `OPENAI_LANGUAGE`               | Language for title generation (e.g., `English`)                            |
| `OPENAI_MODEL`                  | OpenAI model to use (e.g., `gpt-4.1`)                                       |
| `MISTRAL_API_KEY`               | API key for Mistral OCR                                                    |
| `PAPERLESS_API_KEY`             | API key for Paperless-ngx                                                  |
| `PAPERLESS_BASE_URL`            | Base URL of the Paperless-ngx instance (e.g., `http://localhost:8000`)     |
| `PAPERLESS_GENERATE_TITLE_TAG_ID` | Tag ID for documents requiring title generation                            |
| `PAPERLESS_GENERATE_OCR_TAG_ID` | Tag ID for documents requiring OCR processing                              |

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under Apache License 2.0.