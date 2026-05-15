import pdfplumber

def extract_text_from_pdf(path: str) -> str:
    chunks = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            chunks.append(p.extract_text() or "")
    return "\n".join(chunks)
