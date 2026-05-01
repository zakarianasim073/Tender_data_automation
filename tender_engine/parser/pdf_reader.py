"""
PDF Reader
----------
Low-level utility: opens a PDF and returns its text page by page.
Uses pdfplumber for clean text extraction; falls back to PyMuPDF if needed.
"""

import re
from pathlib import Path
from typing import List, Dict


def read_pdf_pages(pdf_path: str) -> List[str]:
    """Return a list of strings, one per page."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages.append(text)
        return pages
    except ImportError:
        pass

    # Fallback: PyMuPDF (fitz)
    try:
        import fitz
        doc = fitz.open(pdf_path)
        pages = [doc[i].get_text() for i in range(len(doc))]
        doc.close()
        return pages
    except ImportError:
        raise ImportError(
            "Neither pdfplumber nor PyMuPDF is installed.\n"
            "Run:  pip install pdfplumber  OR  pip install pymupdf"
        )


def read_pdf_text(pdf_path: str) -> str:
    """Return full text of a PDF as a single string."""
    return "\n".join(read_pdf_pages(pdf_path))


def extract_tables_from_pdf(pdf_path: str) -> List[List[List[str]]]:
    """
    Extract tables page by page using pdfplumber.
    Returns a list (one per page) of tables,
    where each table is a list of rows (list of cell strings).
    """
    try:
        import pdfplumber
        result = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables() or []
                result.append(tables)
        return result
    except ImportError:
        raise ImportError("pdfplumber is required for table extraction. Run: pip install pdfplumber")


def clean_text(text: str) -> str:
    """Normalise whitespace and remove junk characters."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()
