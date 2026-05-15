from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.tender_fields import extract_tender_fields


def extract_from_pdf(path: str, language: str = "en"):
    text = extract_text_from_pdf(path)
    fields = extract_tender_fields(text, language=language)
    return {"text": text[:5000], "fields": fields, "language": language}
