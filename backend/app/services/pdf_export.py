"""TailorResume — Professional ATS PDF Export using ReportLab

Jake's Resume template style:
- Single column, 0.5" margins
- Helvetica 11pt base, 16pt name
- Section headings: bold uppercase + horizontal rule
- Entry: bold title left, date right (same line)
- Italic company left, location right
- Bullets with proper indentation and text wrapping
- Skills: "Category: skill1, skill2" format
"""

import logging
from typing import List, Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import black, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle,
    KeepTogether
)

logger = logging.getLogger(__name__)


def _safe(val: Any) -> str:
    """Safely convert to string, strip None, escape XML entities for ReportLab."""
    if val is None:
        return ""
    s = str(val).strip()
    # Escape XML entities that ReportLab's Paragraph parser needs
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s


def _build_styles():
    """Build paragraph styles matching Jake's Resume template."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ResumeName",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=2,
        textColor=black,
    ))

    styles.add(ParagraphStyle(
        name="ContactInfo",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=HexColor("#333333"),
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=2,
        textColor=black,
    ))

    styles.add(ParagraphStyle(
        name="SummaryText",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="EntryTitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
    ))

    styles.add(ParagraphStyle(
        name="EntrySubtitle",
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=13,
    ))

    styles.add(ParagraphStyle(
        name="EntryDate",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="BulletText",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=1,
    ))

    styles.add(ParagraphStyle(
        name="SkillCategory",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        spaceAfter=2,
    ))

    return styles


def _section_heading(text: str, styles):
    """Return a section heading with horizontal rule."""
    elements = []
    elements.append(Paragraph(_safe(text).upper(), styles["SectionHeading"]))
    elements.append(HRFlowable(
        width="100%", thickness=0.5, color=black,
        spaceBefore=1, spaceAfter=4
    ))
    return elements


def _entry_header_table(left_text: str, right_text: str, styles, bold_left=True, italic_left=False):
    """Create a two-column row: left text + right-aligned date."""
    left_style = "EntryTitle" if bold_left else ("EntrySubtitle" if italic_left else "EntryDate")
    data = [[
        Paragraph(_safe(left_text), styles[left_style]),
        Paragraph(_safe(right_text), styles["EntryDate"]),
    ]]
    page_width = letter[0] - 1 * inch  # total usable width with 0.5" margins
    table = Table(data, colWidths=[page_width * 0.75, page_width * 0.25])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


def _render_header(sec: dict, styles) -> list:
    """Render resume header: name centered + headline + contact info single line."""
    elements = []
    name = _safe(sec.get("fullName"))
    if name:
        elements.append(Paragraph(name, styles["ResumeName"]))

    # Target job title headline
    headline = _safe(sec.get("headline"))
    if headline:
        elements.append(Paragraph(headline, styles["ContactInfo"]))

    # Build contact line
    contact_parts = []
    for field in ("phone", "email", "linkedin", "github", "portfolio", "location"):
        val = sec.get(field)
        if val:
            contact_parts.append(_safe(val))
    if contact_parts:
        elements.append(Paragraph(" | ".join(contact_parts), styles["ContactInfo"]))

    elements.append(Spacer(1, 4))
    return elements


def _render_summary(sec: dict, styles) -> list:
    """Render professional summary section."""
    elements = list(_section_heading(sec.get("name") or "Professional Summary", styles))
    text = _safe(sec.get("text"))
    if text:
        elements.append(Paragraph(text, styles["SummaryText"]))
    return elements


def _render_experience(sec: dict, styles) -> list:
    """Render experience/projects section with entries and bullets."""
    elements = list(_section_heading(sec.get("name") or "Professional Experience", styles))

    for entry in (sec.get("entries") or []):
        if not isinstance(entry, dict):
            continue

        entry_elements = []
        title = _safe(entry.get("title") or entry.get("name"))
        duration = _safe(entry.get("duration") or entry.get("date"))
        company = _safe(entry.get("company"))
        location = _safe(entry.get("location"))

        # Title | Date row
        if title or duration:
            entry_elements.append(_entry_header_table(title, duration, styles, bold_left=True))

        # Company | Location row
        if company or location:
            entry_elements.append(_entry_header_table(company, location, styles, bold_left=False, italic_left=True))

        # Bullets
        for bullet in (entry.get("bullets") or []):
            if isinstance(bullet, str) and bullet.strip():
                # Clean bullet prefix if present
                clean = bullet.strip()
                for prefix in ("- ", "* ", "• ", "– ", "· "):
                    if clean.startswith(prefix):
                        clean = clean[len(prefix):]
                        break
                entry_elements.append(Paragraph(
                    f"\u2022 {_safe(clean)}",
                    styles["BulletText"]
                ))

        entry_elements.append(Spacer(1, 4))

        # Keep each entry together on the same page
        elements.append(KeepTogether(entry_elements))

    return elements


def _render_education(sec: dict, styles) -> list:
    """Render education section."""
    elements = list(_section_heading(sec.get("name") or "Education", styles))

    for entry in (sec.get("entries") or []):
        if not isinstance(entry, dict):
            continue

        entry_elements = []
        degree = _safe(entry.get("degree") or entry.get("title"))
        year = _safe(entry.get("year") or entry.get("duration") or entry.get("date"))
        institution = _safe(entry.get("institution") or entry.get("company"))
        location = _safe(entry.get("location"))

        if degree or year:
            entry_elements.append(_entry_header_table(degree, year, styles, bold_left=True))
        if institution or location:
            entry_elements.append(_entry_header_table(institution, location, styles, bold_left=False, italic_left=True))

        for bullet in (entry.get("bullets") or []):
            if isinstance(bullet, str) and bullet.strip():
                entry_elements.append(Paragraph(f"\u2022 {_safe(bullet)}", styles["BulletText"]))

        entry_elements.append(Spacer(1, 3))
        elements.append(KeepTogether(entry_elements))

    return elements


def _render_skills(sec: dict, styles) -> list:
    """Render skills section with categories."""
    elements = list(_section_heading(sec.get("name") or "Technical Skills", styles))

    cats = sec.get("categories")
    if isinstance(cats, dict) and cats:
        for cat_name, cat_skills in cats.items():
            if isinstance(cat_skills, str):
                skills_str = cat_skills
            elif isinstance(cat_skills, list):
                skills_str = ", ".join(str(s) for s in cat_skills)
            else:
                skills_str = str(cat_skills)
            elements.append(Paragraph(
                f"<b>{_safe(cat_name)}:</b> {_safe(skills_str)}",
                styles["SkillCategory"]
            ))

    items = sec.get("items")
    if isinstance(items, list) and items:
        elements.append(Paragraph(
            _safe(", ".join(str(s) for s in items)),
            styles["SkillCategory"]
        ))

    return elements


def _render_list_section(sec: dict, styles) -> list:
    """Render a list section (certifications, awards, etc.)."""
    elements = list(_section_heading(sec.get("name") or "Additional", styles))

    for item in (sec.get("items") or []):
        if isinstance(item, str) and item.strip():
            elements.append(Paragraph(f"\u2022 {_safe(item)}", styles["BulletText"]))

    return elements


def _render_custom(sec: dict, styles) -> list:
    """Render a custom section."""
    elements = []
    name = sec.get("name")
    if name:
        elements.extend(_section_heading(name, styles))
    text = _safe(sec.get("text"))
    if text:
        elements.append(Paragraph(text, styles["SummaryText"]))
    return elements


async def generate_pdf(resume_sections: List[Dict[str, Any]], template: str = "jake_classic") -> bytes:
    """Generate a professional ATS-friendly PDF using ReportLab.

    Uses Jake's Resume template style:
    - Single column, 0.5" margins, Helvetica
    - Clean section headings with horizontal rules
    - Proper text wrapping and pagination
    """
    import io

    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            title="Resume",
            author="TailorResume",
        )

        styles = _build_styles()
        story = []

        for sec in resume_sections:
            if not isinstance(sec, dict):
                continue
            sec_type = (sec.get("type") or "").lower()

            if sec_type == "header":
                story.extend(_render_header(sec, styles))
            elif sec_type == "summary":
                story.extend(_render_summary(sec, styles))
            elif sec_type in ("experience", "projects"):
                story.extend(_render_experience(sec, styles))
            elif sec_type == "education":
                story.extend(_render_education(sec, styles))
            elif sec_type == "skills":
                story.extend(_render_skills(sec, styles))
            elif sec_type == "list":
                story.extend(_render_list_section(sec, styles))
            elif sec_type == "custom":
                story.extend(_render_custom(sec, styles))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"Generated PDF: {len(pdf_bytes)} bytes")
        return pdf_bytes

    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        raise ValueError(f"Failed to generate PDF: {str(e)}")
