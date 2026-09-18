"""TailorResume — PDF Export using fpdf2 (pure Python, no browser needed)"""

import logging
from typing import List, Dict, Any
from fpdf import FPDF

logger = logging.getLogger(__name__)


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
        self.cell(0, 6, title.upper(), new_x="LMARGIN", new_y="NEXT")
        # Draw underline
        self.set_draw_color(0, 0, 0)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def entry_header(self, left: str, right: str):
        """Render entry header with title left, date right."""
        self.set_font("Helvetica", "B", 10)
        # Calculate widths
        page_width = self.w - self.l_margin - self.r_margin
        self.cell(page_width * 0.7, 5, left, new_x="RIGHT")
        self.set_font("Helvetica", "", 10)
        self.cell(page_width * 0.3, 5, right, align="R", new_x="LMARGIN", new_y="NEXT")

    def entry_subheader(self, left: str, right: str):
        """Render entry subheader (company/location) in italic."""
        self.set_font("Helvetica", "I", 10)
        page_width = self.w - self.l_margin - self.r_margin
        self.cell(page_width * 0.7, 5, left, new_x="RIGHT")
        self.cell(page_width * 0.3, 5, right, align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def bullet_point(self, text: str):
        """Render a bullet point."""
        self.set_font("Helvetica", "", 10)
        bullet = chr(8226)  # •
        indent = 5
        self.set_x(self.l_margin + indent)
        page_width = self.w - self.l_margin - self.r_margin - indent - 3
        self.cell(3, 5, bullet)
        self.multi_cell(page_width, 5, f" {text}")

    def skill_line(self, category: str, skills: str):
        """Render a skill category line."""
        self.set_font("Helvetica", "B", 10)
        cat_width = self.get_string_width(f"{category}: ") + 2
        self.cell(cat_width, 5, f"{category}: ")
        self.set_font("Helvetica", "", 10)
        remaining = self.w - self.l_margin - self.r_margin - cat_width
        self.multi_cell(remaining, 5, skills)


def _safe_str(val: Any) -> str:
    """Safely convert value to string, handling None."""
    if val is None:
        return ""
    return str(val)


async def generate_pdf(resume_sections: List[Dict[str, Any]], template: str = "jake_classic") -> bytes:
    """Generate ATS-friendly PDF bytes from resume sections."""
    pdf = ResumePDF()

    for sec in resume_sections:
        if not isinstance(sec, dict):
            continue
        sec_type = (sec.get("type") or "").lower()

        if sec_type == "header":
            # Name centered, large
            name = _safe_str(sec.get("fullName"))
            if name:
                pdf.set_font("Helvetica", "B", 16)
                pdf.cell(0, 8, name, align="C", new_x="LMARGIN", new_y="NEXT")

            # Contact info centered
            contact_parts = []
            for field in ("email", "phone", "location", "linkedin", "github", "portfolio"):
                val = sec.get(field)
                if val:
                    contact_parts.append(str(val))
            if contact_parts:
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(0, 5, " | ".join(contact_parts), align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

        elif sec_type == "summary":
            pdf.section_title(sec.get("name") or "Professional Summary")
            text = _safe_str(sec.get("text"))
            if text:
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 5, text)

        elif sec_type in ("experience", "projects"):
            pdf.section_title(sec.get("name") or sec_type.title())
            for entry in (sec.get("entries") or []):
                if not isinstance(entry, dict):
                    continue
                title = _safe_str(entry.get("title") or entry.get("name"))
                duration = _safe_str(entry.get("duration") or entry.get("date"))
                company = _safe_str(entry.get("company"))
                location = _safe_str(entry.get("location"))

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
                degree = _safe_str(entry.get("degree") or entry.get("title"))
                year = _safe_str(entry.get("year") or entry.get("duration") or entry.get("date"))
                institution = _safe_str(entry.get("institution") or entry.get("company"))
                location = _safe_str(entry.get("location"))

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
                pdf.multi_cell(0, 5, ", ".join(str(s) for s in items))

        elif sec_type == "list":
            pdf.section_title(sec.get("name") or "Additional")
            for item in (sec.get("items") or []):
                if isinstance(item, str) and item.strip():
                    pdf.bullet_point(item)

        elif sec_type == "custom":
            name = sec.get("name")
            if name:
                pdf.section_title(name)
            text = _safe_str(sec.get("text"))
            if text:
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 5, text)

    return bytes(pdf.output())
