"""TailorResume — Authentic Jake Gutierrez LaTeX Resume Generator & Compiler

Directly clones the gold-standard Jake Gutierrez LaTeX template (jakegut/resume)
and injects candidate's tailored resume sections.
"""

import re
import urllib.request
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def escape_latex(text: Any) -> str:
    """Escape LaTeX special characters."""
    if text is None:
        return ""
    s = str(text).strip()
    # Strip any leading bullet markers
    s = re.sub(r"^[•\-–·*▪►○]\s*", "", s)
    
    replacements = [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    for old, new in replacements:
        s = s.replace(old, new)
    return s


def generate_jake_latex(sections: List[Dict[str, Any]]) -> str:
    """Generate authentic Jake Gutierrez resume.tex from structured sections."""
    header = next((s for s in sections if isinstance(s, dict) and s.get("type") == "header"), {})
    
    full_name = escape_latex(header.get("fullName") or "Candidate Name")
    headline = escape_latex(header.get("headline") or "")
    
    contact_parts = []
    if header.get("phone"):
        contact_parts.append(escape_latex(header["phone"]))
    if header.get("email"):
        email = str(header["email"]).strip()
        contact_parts.append(f"\\href{{mailto:{email}}}{{\\underline{{{escape_latex(email)}}}}}")
    if header.get("linkedin"):
        li = str(header["linkedin"]).strip()
        url = li if li.startswith("http") else f"https://{li}"
        contact_parts.append(f"\\href{{{url}}}{{\\underline{{{escape_latex(li)}}}}}")
    if header.get("github"):
        gh = str(header["github"]).strip()
        url = gh if gh.startswith("http") else f"https://{gh}"
        contact_parts.append(f"\\href{{{url}}}{{\\underline{{{escape_latex(gh)}}}}}")
    if header.get("location"):
        contact_parts.append(escape_latex(header["location"]))
        
    contact_line = " $|$ ".join(contact_parts)
    
    body_sections = []
    
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        sec_type = sec.get("type")
        sec_name = escape_latex(sec.get("name") or "")
        
        # Professional Summary
        if sec_type == "summary":
            text = escape_latex(sec.get("text") or "")
            if text:
                body_sections.append(f"""
\\section{{{sec_name or 'Professional Summary'}}}
\\small{{{text}}}
""")
                
        # Technical Skills
        elif sec_type == "skills":
            cats = sec.get("categories") or {}
            skills_lines = []
            if isinstance(cats, dict) and cats:
                for cat_name, cat_val in cats.items():
                    val_str = cat_val if isinstance(cat_val, str) else ", ".join(str(x) for x in cat_val)
                    skills_lines.append(f"\\textbf{{{escape_latex(cat_name)}}}{{: {escape_latex(val_str)}}} \\\\")
            
            items = sec.get("items") or sec.get("list_items") or []
            if items:
                skills_lines.append(escape_latex(", ".join(str(i) for i in items)))
            
            skills_content = "\n     ".join(skills_lines)
            body_sections.append(f"""
\\section{{{sec_name or 'Technical Skills'}}}
 \\begin{{itemize}}[leftmargin=0.15in, label={{}}]
    \\small{{\\item{{
     {skills_content}
    }}}}
 \\end{{itemize}}
""")
            
        # Professional Experience
        elif sec_type == "experience":
            entries = sec.get("entries") or []
            exp_items = []
            for e in entries:
                if not isinstance(e, dict):
                    continue
                title = escape_latex(e.get("title") or e.get("name") or "")
                date = escape_latex(e.get("duration") or e.get("date") or "")
                company = escape_latex(e.get("company") or "")
                loc = escape_latex(e.get("location") or "")
                
                bullets = e.get("bullets") or []
                bullet_items = "\n        ".join([f"\\resumeItem{{{escape_latex(b)}}}" for b in bullets if b and str(b).strip()])
                
                exp_items.append(f"""    \\resumeSubheading
      {{{title}}}{{{date}}}
      {{{company}}}{{{loc}}}
      \\resumeItemListStart
        {bullet_items}
      \\resumeItemListEnd""")
            
            exp_joined = "\n\n".join(exp_items)
            body_sections.append(f"""
\\section{{{sec_name or 'Experience'}}}
  \\resumeSubHeadingListStart
{exp_joined}
  \\resumeSubHeadingListEnd
""")
            
        # Projects
        elif sec_type == "projects":
            entries = sec.get("entries") or []
            proj_items = []
            for e in entries:
                if not isinstance(e, dict):
                    continue
                title = escape_latex(e.get("title") or e.get("name") or "")
                date = escape_latex(e.get("duration") or e.get("date") or "")
                tech = escape_latex(e.get("company") or "")
                heading_left = f"\\textbf{{{title}}}"
                if tech:
                    heading_left += f" $|$ \\emph{{{tech}}}"
                
                bullets = e.get("bullets") or []
                bullet_items = "\n            ".join([f"\\resumeItem{{{escape_latex(b)}}}" for b in bullets if b and str(b).strip()])
                
                proj_items.append(f"""      \\resumeProjectHeading
          {{{heading_left}}}{{{date}}}
          \\resumeItemListStart
            {bullet_items}
          \\resumeItemListEnd""")
                
            proj_joined = "\n".join(proj_items)
            body_sections.append(f"""
\\section{{{sec_name or 'Projects'}}}
    \\resumeSubHeadingListStart
{proj_joined}
    \\resumeSubHeadingListEnd
""")
            
        # Education
        elif sec_type == "education":
            entries = sec.get("entries") or []
            edu_items = []
            for e in entries:
                if not isinstance(e, dict):
                    continue
                inst = escape_latex(e.get("institution") or e.get("company") or "")
                loc = escape_latex(e.get("location") or "")
                degree = escape_latex(e.get("degree") or e.get("title") or "")
                date = escape_latex(e.get("year") or e.get("duration") or e.get("date") or "")
                
                edu_items.append(f"""    \\resumeSubheading
      {{{inst}}}{{{loc}}}
      {{{degree}}}{{{date}}}""")
                
            edu_joined = "\n".join(edu_items)
            body_sections.append(f"""
\\section{{{sec_name or 'Education'}}}
  \\resumeSubHeadingListStart
{edu_joined}
  \\resumeSubHeadingListEnd
""")
            
        # Certifications / Achievements / Additional
        elif sec_type in ("list", "custom"):
            items = sec.get("items") or sec.get("list_items") or []
            text = sec.get("text") or ""
            if not items and text:
                items = [p.strip() for p in text.split("\n") if p.strip()]
            
            if items:
                bullet_items = "\n    ".join([f"\\resumeItem{{{escape_latex(i)}}}" for i in items if i and str(i).strip()])
                body_sections.append(f"""
\\section{{{sec_name or 'Certifications'}}}
  \\resumeItemListStart
    {bullet_items}
  \\resumeItemListEnd
""")

    body_content = "\n".join(body_sections)

    # Full authentic Jake Gutierrez LaTeX template with standard font, margin and glyphtounicode
    tex = f"""%-------------------------
% Resume in Latex - Jake Gutierrez Template
% Auto-generated by TailorResume (https://github.com/naamsanamone/TailorResume)
% License : MIT
%------------------------

\\documentclass[letterpaper,11pt]{{article}}

\\usepackage{{latexsym}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{titlesec}}
\\usepackage{{marvosym}}
\\usepackage[usenames,dvipsnames]{{color}}
\\usepackage{{verbatim}}
\\usepackage{{enumitem}}
\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage[english]{{babel}}
\\usepackage{{tabularx}}
\\input{{glyphtounicode}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyfoot{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}

% Adjust margins (0.5 inch all sides)
\\addtolength{{\\oddsidemargin}}{{-0.5in}}
\\addtolength{{\\evensidemargin}}{{-0.5in}}
\\addtolength{{\\textwidth}}{{1in}}
\\addtolength{{\\topmargin}}{{-.5in}}
\\addtolength{{\\textheight}}{{1.0in}}

\\urlstyle{{same}}

\\raggedbottom
\\raggedright
\\setlength{{\\tabcolsep}}{{0in}}

% Sections formatting
\\titleformat{{\\section}}{{
  \\vspace{{-4pt}}\\scshape\\raggedright\\large
}}{{}}{{0em}}{{}}[\\color{{black}}\\titlerule \\vspace{{-5pt}}]

% Ensure generated PDF is machine readable / ATS parsable
\\pdfgentounicode=1

% Custom commands
\\newcommand{{\\resumeItem}}[1]{{
  \\item\\small{{
    {{#1 \\vspace{{-2pt}}}}
  }}
}}

\\newcommand{{\\resumeSubheading}}[4]{{
  \\vspace{{-2pt}}\\item
    \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
      \\textbf{{#1}} & #2 \\\\
      \\textit{{\\small#3}} & \\textit{{\\small #4}} \\\\
    \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\newcommand{{\\resumeProjectHeading}}[2]{{
    \\item
    \\begin{{tabular*}}{{0.97\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
      \\small#1 & #2 \\\\
    \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\renewcommand\\labelitemii{{$\\vcenter{{\\hbox{{\\tiny$\\bullet$}}}}$}}

\\newcommand{{\\resumeSubHeadingListStart}}{{\\begin{{itemize}}[leftmargin=0.15in, label={{}}]}}
\\newcommand{{\\resumeSubHeadingListEnd}}{{\\end{{itemize}}}}
\\newcommand{{\\resumeItemListStart}}{{\\begin{{itemize}}}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\vspace{{-5pt}}}}

\\begin{{document}}

%----------HEADING----------
\\begin{{center}}
    \\textbf{{\\Huge \\scshape {full_name}}} \\\\ \\vspace{{1pt}}
    \\small {contact_line}
\\end{{center}}

{body_content}

\\end{{document}}
"""
    return tex


def compile_latex_to_pdf(latex_code: str) -> bytes:
    """Compile LaTeX source code into authentic vector PDF using TeX Live engine."""
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    parts = [
        f'--{boundary}',
        'Content-Disposition: form-data; name="engine"',
        '',
        'pdflatex',
        f'--{boundary}',
        'Content-Disposition: form-data; name="return"',
        '',
        'pdf',
        f'--{boundary}',
        'Content-Disposition: form-data; name="filename[]"',
        '',
        'document.tex',
        f'--{boundary}',
        'Content-Disposition: form-data; name="filecontents[]"',
        '',
        latex_code,
        f'--{boundary}--',
        ''
    ]
    body = '\r\n'.join(parts).encode('utf-8')

    req = urllib.request.Request(
        'https://texlive.net/cgi-bin/latexcgi',
        data=body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) TailorResume/1.0'
        }
    )
    resp = urllib.request.urlopen(req, timeout=35)
    pdf_bytes = resp.read()
    if pdf_bytes.startswith(b'%PDF'):
        logger.info(f"Successfully compiled Jake's Resume LaTeX PDF: {len(pdf_bytes)} bytes")
        return pdf_bytes
    else:
        error_msg = pdf_bytes[:300].decode('utf-8', errors='ignore')
        logger.error(f"TeX Live compile error: {error_msg}")
        raise ValueError(f"LaTeX compilation failed: {error_msg}")
