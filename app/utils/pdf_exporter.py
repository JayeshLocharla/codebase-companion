"""
PDF report generation utility.

Changes from original:
- Returns PDF bytes directly instead of a temp file path.
  This eliminates the ``delete=False`` temp file leak where the caller was
  responsible for cleanup but never performed it.
- Callers that need a file (e.g. Streamlit download_button) can use
  ``io.BytesIO(generate_pdf_report(output))`` directly.
"""

import io
import logging

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER

logger = logging.getLogger(__name__)


def generate_pdf_report(output_dict: dict) -> bytes:
    """
    Build a PDF report from agent output and return it as raw bytes.

    Args:
        output_dict: Mapping of section title → content string.

    Returns:
        PDF file contents as bytes.
    """
    styles = getSampleStyleSheet()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)

    elements = []
    for section, content in output_dict.items():
        elements.append(Paragraph(f"<b>{section}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        # Escape special XML characters then convert newlines to HTML breaks
        safe_content = (
            content
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )
        elements.append(Paragraph(safe_content, styles["BodyText"]))
        elements.append(Spacer(1, 24))

    doc.build(elements)
    logger.info("PDF report generated (%d sections)", len(output_dict))
    return buffer.getvalue()
