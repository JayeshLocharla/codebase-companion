# app/utils/pdf_exporter.py

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
import tempfile

def generate_pdf_report(output_dict: dict) -> str:
    """
    Generate a PDF from agent output dict and return path to the temp file.
    """
    styles = getSampleStyleSheet()
    buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(buffer.name, pagesize=LETTER)

    elements = []

    for section, content in output_dict.items():
        elements.append(Paragraph(f"<b>{section}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 12))

        # Convert newlines to HTML breaks
        content = content.replace("\n", "<br/>")
        elements.append(Paragraph(content, styles["BodyText"]))
        elements.append(Spacer(1, 24))

    doc.build(elements)
    return buffer.name
