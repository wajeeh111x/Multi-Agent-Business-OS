from pathlib import Path
from pypdf import PdfReader


def load_pdf(file_path: str) -> str:
    """
    Read a PDF and return all extracted text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"{file_path} not found.")

    reader = PdfReader(path)

    full_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            full_text += text + "\n"

    return full_text.strip()