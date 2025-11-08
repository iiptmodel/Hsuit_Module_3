"""
Medical Document Parser Service

This module provides robust PDF and document parsing with multiple fallback strategies:
1. Docling structured parsing (primary)
2. PDF sanitization + retry (secondary)
3. OCR fallback for scanned documents (tertiary)

Dependencies:
    - docling: For structured document parsing
    - pypdf: For PDF manipulation and sanitization
    - pdf2image: For converting PDF pages to images
    - pytesseract: For OCR text extraction

Author: Medical Report Analysis System
"""

import os
import logging

# Prevent symlink permission issues on Windows
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

from docling.document_converter import DocumentConverter
from docling.exceptions import ConversionError
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path
import pytesseract

logger = logging.getLogger(__name__)

# Check for ONNX Runtime availability
try:
    import onnxruntime  # type: ignore
    logger.info("onnxruntime is available and may be used by Docling/ONNX models.")
except ImportError:
    logger.warning(
        "onnxruntime is NOT installed. "
        "Install it for best layout detection via ONNXRuntime."
    )

_converter = None  # lazy singleton

def get_converter() -> DocumentConverter:
    """Lazily initialize and return the Docling converter.

    Avoids blocking import/startup; initializes on first use.
    """
    global _converter
    if _converter is None:
        logger.info("Initializing Docling converter (lazy)...")
        try:
            _converter = DocumentConverter()
            logger.info("Docling converter initialized.")
        except Exception as e:
            logger.error(f"Docling initialization FAILED: {e}", exc_info=True)
            raise
    return _converter


def sanitize_pdf(path: str) -> str:
    """
    Sanitize a potentially corrupted PDF by rewriting its structure.
    
    This function reads a PDF file and rewrites all its pages to a new file,
    which can fix certain types of PDF corruption or formatting issues.
    
    Args:
        path: Absolute path to the PDF file to sanitize
        
    Returns:
        str: Path to the sanitized PDF file (ends with _clean.pdf)
             Returns original path if sanitization fails
             
    Example:
        >>> clean_path = sanitize_pdf("report.pdf")
        >>> print(clean_path)  # "report_clean.pdf"
    """
    try:
        reader = PdfReader(path)
        writer = PdfWriter()

        # Copy all pages to new PDF
        for page in reader.pages:
            writer.add_page(page)

        # Write sanitized PDF
        new_path = path.replace(".pdf", "_clean.pdf")
        with open(new_path, "wb") as f:
            writer.write(f)

        logger.info(f"PDF sanitized successfully: {new_path}")
        return new_path

    except Exception as e:
        logger.error(f"Failed to sanitize PDF: {e}", exc_info=True)
        return path  # Return original if sanitization fails


def ocr_pdf(path: str) -> str:
    """
    Extract text from PDF using Optical Character Recognition (OCR).
    
    This function converts each PDF page to an image and uses Tesseract OCR
    to extract text. Useful for scanned documents or image-based PDFs.
    
    Args:
        path: Absolute path to the PDF file
        
    Returns:
        str: Extracted text from all pages, joined with newlines
             Returns empty string if OCR fails
             
    Note:
        Requires Tesseract OCR to be installed on the system.
        For Windows: https://github.com/UB-Mannheim/tesseract/wiki
        
    Example:
        >>> text = ocr_pdf("scanned_report.pdf")
        >>> print(len(text))  # Number of characters extracted
    """
    try:
        # Convert PDF pages to images at 200 DPI
        pages = convert_from_path(path, dpi=200)
        
        # Extract text from each page image
        text = "\n".join(pytesseract.image_to_string(page) for page in pages)
        
        logger.info(f"OCR extracted {len(text)} chars from {len(pages)} pages")
        return text
        
    except Exception as e:
        logger.error(f"OCR failed: {e}", exc_info=True)
        return ""


def extract_data_from_file(file_path: str) -> str:
    """
    Extract text from medical documents using multi-tier fallback strategy.
    
    Processing Pipeline:
        1. Attempt structured parsing with Docling
        2. If fails: Sanitize PDF and retry Docling
        3. If still fails: Use OCR fallback
        4. If all fail: Return helpful error message
    
    Args:
        file_path: Absolute path to the document file
                   Supports: PDF, images (PNG, JPG, etc.)
        
    Returns:
        str: Extracted text content from the document
             May include markdown formatting from Docling
             Returns error message string if extraction fails
             
    Raises:
        Does not raise exceptions - returns error strings instead
        
    Example:
        >>> text = extract_data_from_file("medical_report.pdf")
        >>> if text.startswith("Error:"):
        ...     print("Extraction failed:", text)
        ... else:
        ...     print(f"Extracted {len(text)} characters")
    """
    logger.info(f"Extracting data from file: {file_path}")

    # Validate file exists
    if not os.path.exists(file_path):
        error_msg = f"Error: File does not exist. {file_path}"
        logger.error(error_msg)
        return error_msg

    # --- TIER 1: Structured Docling Parsing ---
    try:
        logger.info("Converting document with Docling...")
        converter = get_converter()
        result = converter.convert(file_path)
        content = result.document.export_to_markdown()

        if content and content.strip():
            logger.info(f"Docling extracted {len(content)} chars (structured).")
            return content.strip()

        logger.warning("Docling returned EMPTY text. Falling back...")

    except ConversionError:
        # --- TIER 2: PDF Sanitization + Retry ---
        logger.warning("Docling ConversionError — attempting PDF sanitization...")
        clean_path = sanitize_pdf(file_path)

        try:
            converter = get_converter()
            result = converter.convert(clean_path)
            content = result.document.export_to_markdown()

            if content and content.strip():
                logger.info(
                    f"Sanitized Docling extracted {len(content)} chars."
                )
                return content.strip()

        except Exception as sanitize_error:
            logger.warning(
                f"Docling STILL failed after sanitization: {sanitize_error}"
            )

    except Exception as e:
        logger.error(f"Docling error: {e}", exc_info=True)

    # --- TIER 3: OCR Fallback ---
    logger.warning("Attempting OCR fallback...")
    text = ocr_pdf(file_path)

    if text and text.strip():
        logger.info(f"OCR fallback successful: {len(text)} chars extracted")
        return text.strip()

    # --- FINAL FAILURE ---
    logger.error("All parsing methods failed.")
    return (
        "Error: Could not extract text from this document. "
        "The file may be corrupted, password-protected, or in an unsupported format. "
        "Try uploading a scanned image (PNG/JPG) of each page instead."
    )

