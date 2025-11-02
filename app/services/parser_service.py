# app/services/parser_service.py
from docling.document_converter import DocumentConverter
import logging
import os

# Disable symlinks for Windows compatibility
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

logger = logging.getLogger(__name__)

# Initialize Docling converter
logger.info("Initializing Docling converter...")
try:
    converter = DocumentConverter()
    logger.info("Docling converter initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Docling converter: {e}", exc_info=True)
    raise

def extract_data_from_file(file_path: str) -> str:
    """
    Uses Docling to parse a PDF/image and extract structured data.
    Returns a string of extracted text for the summarizer.
    """
    logger.info(f"Extracting data from file: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return f"Error: File does not exist. {file_path}"

    try:
        logger.info("Converting document with Docling...")
        doc = converter.convert(file_path)
        logger.info(f"Document converted successfully. Pages: {len(doc.pages)}, Tables: {len(doc.tables)}")

        # Extract text from all pages
        extracted_text = ""
        for i, page in enumerate(doc.pages):
            page_text = page.text.strip()
            if page_text:
                extracted_text += f"Page {i+1}:\n{page_text}\n\n"
                logger.debug(f"Extracted text from page {i+1}: {len(page_text)} characters")

        # For tables, if any
        for i, table in enumerate(doc.tables):
            table_md = table.export_to_markdown()
            if table_md.strip():
                extracted_text += f"Table {i+1}:\n{table_md}\n\n"
                logger.debug(f"Extracted table {i+1}: {len(table_md)} characters")

        final_text = extracted_text.strip()
        logger.info(f"Text extraction completed. Total characters: {len(final_text)}")
        logger.info(f"Extracted text preview: {final_text[:500]}")
        return final_text

    except Exception as e:
        logger.error(f"Docling parsing failed for {file_path}: {e}", exc_info=True)
        return f"Error: Could not parse document. {str(e)}"
