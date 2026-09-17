import logging
from typing import List, Dict, Any
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Resume</title>
    <style>
        @page {{
            size: letter;
            margin: 0.5in;
        }}
        body {{
            font-family: 'Calibri', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.3;
            color: #000;
            margin: 0;
            padding: 0;
        }}
        h1, h2, h3, h4, p, ul {{
            margin: 0;
            padding: 0;
        }}
        .header {{
            text-align: center;
            margin-bottom: 12pt;
        }}
        .header h1 {{
            font-size: 16pt;
            text-transform: uppercase;
            font-weight: bold;
            margin-bottom: 4pt;
        }}
        .contact-info {{
            font-size: 10pt;
        }}
        .section {{
            margin-bottom: 12pt;
        }}
        .section-title {{
            font-size: 12pt;
            font-weight: bold;
            text-transform: uppercase;
            border-bottom: 1pt solid #000;
            margin-bottom: 6pt;
            padding-bottom: 2pt;
        }}
        .entry {{
            margin-bottom: 8pt;
        }}
        .entry-header {{
            display: flex;
            justify-content: space-between;
            font-weight: bold;
        }}
        .entry-subheader {{
            display: flex;
            justify-content: space-between;
            font-style: italic;
            margin-bottom: 4pt;
        }}
        ul {{
            margin-left: 15pt;
        }}
        li {{
            margin-bottom: 3pt;
        }}
        .skills-category {{
            margin-bottom: 4pt;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

def render_html(sections: List[Dict[str, Any]]) -> str:
    content = ""
    for sec in sections:
        sec_type = sec.get("type", "").lower()
        if sec_type == "header":
            content += f"""
            <div class="header">
                <h1>{sec.get('fullName', '')}</h1>
                <div class="contact-info">
                    {sec.get('email', '')} | {sec.get('phone', '')} | {sec.get('location', '')}
                </div>
            </div>
            """
        elif sec_type == "summary":
            content += f"""
            <div class="section">
                <div class="section-title">{sec.get('name', 'Professional Summary')}</div>
                <p>{sec.get('text', '')}</p>
            </div>
            """
        elif sec_type in ["experience", "education", "projects"]:
            content += f"""
            <div class="section">
                <div class="section-title">{sec.get('name', sec_type.title())}</div>
            """
            for entry in sec.get("entries", []):
                title = entry.get("title", "") or entry.get("degree", "") or entry.get("name", "")
                org = entry.get("company", "") or entry.get("institution", "")
                date = entry.get("date", "")
                loc = entry.get("location", "")
                
                content += f"""
                <div class="entry">
                    <div class="entry-header">
                        <span>{title}</span>
                        <span>{date}</span>
                    </div>
                    <div class="entry-subheader">
                        <span>{org}</span>
                        <span>{loc}</span>
                    </div>
                """
                bullets = entry.get("bullets", [])
                if bullets:
                    content += "<ul>"
                    for b in bullets:
                        content += f"<li>{b}</li>"
                    content += "</ul>"
                content += "</div>"
            content += "</div>"
        elif sec_type == "skills":
            content += f"""
            <div class="section">
                <div class="section-title">{sec.get('name', 'Skills')}</div>
            """
            cats = sec.get("categories", [])
            if cats:
                for cat in cats:
                    content += f"""
                    <div class="skills-category">
                        <strong>{cat.get('name', '')}:</strong> {", ".join(cat.get('items', []))}
                    </div>
                    """
            elif sec.get("items"):
                content += f"<p>{', '.join(sec.get('items', []))}</p>"
            content += "</div>"
    return HTML_TEMPLATE.format(content=content)


async def generate_pdf(resume_sections: List[Dict[str, Any]], template: str = 'jake_classic') -> bytes:
    """Generate PDF bytes using Playwright."""
    html_content = render_html(resume_sections)
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_content(html_content)
            pdf_bytes = await page.pdf(format="Letter", print_background=True, margin={"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"})
            await browser.close()
            return pdf_bytes
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise ValueError("Failed to generate PDF")
