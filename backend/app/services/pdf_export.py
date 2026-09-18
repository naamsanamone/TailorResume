"""TailorResume — PDF Export using fpdf2 (pure Python, no browser needed)"""

import os
import re
import logging
from typing import List, Dict, Any
from fpdf import FPDF

logger = logging.getLogger(__name__)


def _sanitize(text: Any) -> str:
    """Remove or replace Unicode chars that aren't in standard PDF fonts."""
    if text is None:
        return ""
    s = str(text)
    # Replace common unicode chars with ASCII equivalents
    replacements = {
        "\u2022": "-",   # •
        "\u2013": "-",   # –
        "\u2014": "-",   # —
        "\u2018": "'",   # '
        "\u2019": "'",   # '
        "\u201c": '"',   # "
        "\u201d": '"',   # "
        "\u2026": "...", # …
        "\u00b7": "-",   # ·
        "\u25aa": "-",   # ▪
        "\u25ba": "-",   # ►
        "\u25cb": "-",   # ○
        "\u2192": "->",  # →
        "\u00a0": " ",   # non-breaking space
        "\u200b": "",    # zero-width space
        "\u00e9": "e",   # é
        "\u00e8": "e",   # è
        "\u00f1": "n",   # ñ
        "\ud83d": "",    # emoji range start
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    # Strip any remaining non-ASCII chars
    s = s.encode("ascii", errors="ignore").decode("ascii")
    return s.strip()


class ResumePDF(FPDF):
    """Custom PDF class for ATS-friendly resume generation."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_margins(12.7, 12.7, 12.7)  # 0.5 inch margins
        self.set_font("Helvetica", size=10)

    def section_title(self, title: str):
        """Render a section heading with underline."""
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 6, _sanitize(title).upper(), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 0, 0)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def entry_header(self, left: str, right: str):
        """Render entry header with title left, date right."""
        self.set_font("Helvetica", "B", 10)
        page_width = self.w - self.l_margin - self.r_margin
        self.cell(page_width * 0.7, 5, _sanitize(left), new_x="RIGHT")
        self.set_font("Helvetica", "", 10)
        self.cell(page_width * 0.3, 5, _sanitize(right), align="R", new_x="LMARGIN", new_y="NEXT")

    def entry_subheader(self, left: str, right: str):
        """Render entry subheader (company/location) in italic."""
        self.set_font("Helvetica", "I", 10)
        page_width = self.w - self.l_margin - self.r_margin
        self.cell(page_width * 0.7, 5, _sanitize(left), new_x="RIGHT")
        self.cell(page_width * 0.3, 5, _sanitize(right), align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def bullet_point(self, text: str):
        """Render a bullet point."""
        self.set_font("Helvetica", "", 10)
        indent = 5
        self.set_x(self.l_margin + indent)
        page_width = self.w - self.l_margin - self.r_margin - indent - 3
        self.cell(3, 5, "-")
        self.multi_cell(page_width, 5, f" {_sanitize(text)}")

    def skill_line(self, category: str, skills: str):
        """Render a skill category line."""
        self.set_font("Helvetica", "B", 10)
        cat_text = f"{_sanitize(category)}: "
        cat_width = self.get_string_width(cat_text) + 2
        self.cell(cat_width, 5, cat_text)
        self.set_font("Helvetica", "", 10)
        remaining = self.w - self.l_margin - self.r_margin - cat_width
        self.multi_cell(remaining, 5, _sanitize(skills))


async def generate_pdf(resume_sections: List[Dict[str, Any]], template: str = "jake_classic") -> bytes:
    """Generate ATS-friendly PDF bytes from resume sections."""
    try:
        pdf = ResumePDF()

        for sec in resume_sections:
            if not isinstance(sec, dict):
                continue
            sec_type = (sec.get("type") or "").lower()

            if sec_type == "header":
                name = _sanitize(sec.get("fullName"))
                if name:
                    pdf.set_font("Helvetica", "B", 16)
                    pdf.cell(0, 8, name, align="C", new_x="LMARGIN", new_y="NEXT")

                contact_parts = []
                for field in ("email", "phone", "location", "linkedin", "github", "portfolio"):
                    val = sec.get(field)
                    if val:
                        contact_parts.append(_sanitize(val))
                if contact_parts:
                    pdf.set_font("Helvetica", "", 9)
                    pdf.cell(0, 5, " | ".join(contact_parts), align="C", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(2)

            elif sec_type == "summary":
                pdf.section_title(sec.get("name") or "Professional Summary")
                text = _sanitize(sec.get("text"))
                if text:
                    pdf.set_font("Helvetica", "", 10)
                    pdf.multi_cell(0, 5, text)

            elif sec_type in ("experience", "projects"):
                pdf.section_title(sec.get("name") or sec_type.title())
                for entry in (sec.get("entries") or []):
                    if not isinstance(entry, dict):
                        continue
                    title = _sanitize(entry.get("title") or entry.get("name"))
                    duration = _sanitize(entry.get("duration") or entry.get("date"))
                    company = _sanitize(entry.get("company"))
                    location = _sanitize(entry.get("location"))

                    pdf.entry_header(title, duration)
                    if company or location:
                        pdf.entry_subheader(company, location)

                    for bullet in (entry.get("bullets") or []):
                        if isinstance(bullet, str) and bullet.strip():
                            pdf.bullet_point(bullet)
                    pdf.ln(1)

            elif sec_type == "education":
                pdf.section_title(sec.get("name") or "Education")
                for entry in (sec.get("entries") or []):
                    if not isinstance(entry, dict):
                        continue
                    degree = _sanitize(entry.get("degree") or entry.get("title"))
                    year = _sanitize(entry.get("year") or entry.get("duration") or entry.get("date"))
                    institution = _sanitize(entry.get("institution") or entry.get("company"))
                    location = _sanitize(entry.get("location"))

                    pdf.entry_header(degree, year)
                    if institution or location:
                        pdf.entry_subheader(institution, location)

                    for bullet in (entry.get("bullets") or []):
                        if isinstance(bullet, str) and bullet.strip():
                            pdf.bullet_point(bullet)

            elif sec_type == "skills":
                pdf.section_title(sec.get("name") or "Skills")
                cats = sec.get("categories")
                if isinstance(cats, dict) and cats:
                    for cat_name, cat_skills in cats.items():
                        skills_str = cat_skills if isinstance(cat_skills, str) else ", ".join(str(s) for s in cat_skills)
                        pdf.skill_line(str(cat_name), skills_str)
                items = sec.get("items")
                if isinstance(items, list) and items:
                    pdf.set_font("Helvetica", "", 10)
                    pdf.multi_cell(0, 5, _sanitize(", ".join(str(s) for s in items)))

            elif sec_type == "list":
                pdf.section_title(sec.get("name") or "Additional")
                for item in (sec.get("items") or []):
                    if isinstance(item, str) and item.strip():
                        pdf.bullet_point(item)

            elif sec_type == "custom":
                name = sec.get("name")
                if name:
                    pdf.section_title(name)
                text = _sanitize(sec.get("text"))
                if text:
                    pdf.set_font("Helvetica", "", 10)
                    pdf.multi_cell(0, 5, text)

        return bytes(pdf.output())
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise ValueError(f"Failed to generate PDF: {str(e)}")
