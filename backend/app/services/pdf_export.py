"""TailorResume — PDF Export using HTML Templates + xhtml2pdf

Approach: Jinja2 renders resume data into HTML template → xhtml2pdf converts to PDF.
This is the same approach used by OpenResume, Reactive Resume, and commercial builders.
"""

import io
import os
import logging
from typing import List, Dict, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa

logger = logging.getLogger(__name__)

# Template directory
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

# Available templates
TEMPLATES = {
    "jake_classic": "jake_classic.html",
    "default": "jake_classic.html",
}


def _get_jinja_env() -> Environment:
    """Create Jinja2 environment with template directory."""
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
    )


def _prepare_sections(resume_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean and prepare resume sections for template rendering."""
    cleaned = []
    for sec in resume_sections:
        if not isinstance(sec, dict):
            continue
        # Ensure all fields have safe defaults
        section = dict(sec)
        section.setdefault("type", "custom")
        section.setdefault("name", "")
        section.setdefault("text", "")
        section.setdefault("entries", [])
        section.setdefault("items", [])
        section.setdefault("categories", {})

        # Clean entries
        if section.get("entries"):
            clean_entries = []
            for entry in section["entries"]:
                if isinstance(entry, dict):
                    e = dict(entry)
                    e.setdefault("title", "")
                    e.setdefault("company", "")
                    e.setdefault("location", "")
                    e.setdefault("duration", e.get("date", ""))
                    e.setdefault("degree", "")
                    e.setdefault("institution", e.get("company", ""))
                    e.setdefault("year", e.get("duration", ""))
                    e.setdefault("bullets", [])
                    # Filter empty bullets
                    e["bullets"] = [b for b in e["bullets"] if isinstance(b, str) and b.strip()]
                    clean_entries.append(e)
            section["entries"] = clean_entries

        # Clean items — rename to list_items to avoid Jinja2 dict.items() conflict
        raw_items = section.pop("items", []) or []
        section["list_items"] = [i for i in raw_items if isinstance(i, str) and i.strip()]

        cleaned.append(section)
    return cleaned


def render_html(resume_sections: List[Dict[str, Any]], template_name: str = "jake_classic") -> str:
    """Render resume sections into HTML using a Jinja2 template."""
    env = _get_jinja_env()
    template_file = TEMPLATES.get(template_name, TEMPLATES["default"])
    template = env.get_template(template_file)

    sections = _prepare_sections(resume_sections)

    html = template.render(sections=sections)
    return html


async def generate_pdf(resume_sections: List[Dict[str, Any]], template: str = "jake_classic") -> bytes:
    """Generate ATS-friendly PDF from resume sections using HTML template.

    Pipeline: Resume JSON → Jinja2 HTML Template → xhtml2pdf → PDF bytes
    """
    try:
        # Render HTML
        html_content = render_html(resume_sections, template)

        # Convert HTML to PDF
        buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            src=html_content,
            dest=buffer,
            encoding="utf-8",
        )

        if pisa_status.err:
            logger.error(f"xhtml2pdf reported {pisa_status.err} errors")

        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"Generated PDF: {len(pdf_bytes)} bytes using template '{template}'")
        return pdf_bytes

    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        raise ValueError(f"Failed to generate PDF: {str(e)}")
