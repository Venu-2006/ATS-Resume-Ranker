import fitz
from docx import Document


def extract_pdf_text(pdf_file):

    pdf = fitz.open(
        stream=pdf_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in pdf:
        text += page.get_text()

    return text


def extract_docx_text(docx_file):

    doc = Document(docx_file)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def extract_text(file):

    filename = file.name.lower()

    if filename.endswith(".pdf"):
        return extract_pdf_text(file)

    elif filename.endswith(".docx"):
        return extract_docx_text(file)

    else:
        raise Exception(
            f"Unsupported file type: {filename}"
        )

