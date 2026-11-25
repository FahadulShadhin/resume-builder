from __future__ import annotations

import re
from html import escape
from io import BytesIO
from pathlib import Path
from typing import Callable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Table,
    TableStyle,
)

from src.models import Education, Experience, Project, Resume

PAGE_SIZES = {"LETTER": LETTER, "A4": A4}
LINK_BLUE = colors.HexColor("#0000ee")
RULE_COLOR = colors.HexColor("#777777")


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()["Normal"]
    return {
        "name": ParagraphStyle(
            "ResumeName",
            parent=base,
            fontName="Times-Roman",
            fontSize=22,
            leading=25,
            alignment=TA_CENTER,
            spaceAfter=1,
        ),
        "contact": ParagraphStyle(
            "ResumeContact",
            parent=base,
            fontName="Times-Roman",
            fontSize=9.4,
            leading=11,
            alignment=TA_CENTER,
            spaceAfter=7,
        ),
        "section": ParagraphStyle(
            "ResumeSection",
            parent=base,
            fontName="Times-Bold",
            fontSize=11.5,
            leading=14,
            spaceBefore=4,
            spaceAfter=1,
        ),
        "body": ParagraphStyle(
            "ResumeBody",
            parent=base,
            fontName="Times-Roman",
            fontSize=10,
            leading=11.8,
            alignment=TA_LEFT,
            spaceAfter=1,
            allowWidows=0,
            allowOrphans=0,
        ),
        "position": ParagraphStyle(
            "ResumePosition",
            parent=base,
            fontName="Times-Bold",
            fontSize=11.2,
            leading=12,
            spaceBefore=2,
            spaceAfter=0,
        ),
        "meta": ParagraphStyle(
            "ResumeMeta",
            parent=base,
            fontName="Times-Italic",
            fontSize=10.4,
            leading=11.5,
            spaceAfter=0,
        ),
        "meta_right": ParagraphStyle(
            "ResumeMetaRight",
            parent=base,
            fontName="Times-Italic",
            fontSize=10.4,
            leading=11.5,
            alignment=TA_RIGHT,
        ),
        "education_left": ParagraphStyle(
            "ResumeEducationLeft",
            parent=base,
            fontName="Times-Bold",
            fontSize=10.2,
            leading=11.5,
        ),
        "education_right": ParagraphStyle(
            "ResumeEducationRight",
            parent=base,
            fontName="Times-Bold",
            fontSize=9.6,
            leading=11.5,
            alignment=TA_RIGHT,
        ),
        "bullet": ParagraphStyle(
            "ResumeBullet",
            parent=base,
            fontName="Times-Roman",
            fontSize=10,
            leading=11.8,
            leftIndent=9,
            firstLineIndent=-8,
            bulletIndent=0,
            spaceAfter=0.5,
            allowWidows=0,
            allowOrphans=0,
        ),
    }


def _bold_metrics(text: str, metrics: list[str]) -> str:
    escaped = escape(text)
    for metric in sorted(set(metrics), key=len, reverse=True):
        safe_metric = escape(metric)
        if safe_metric:
            escaped = re.sub(
                re.escape(safe_metric),
                lambda match: f"<b>{match.group(0)}</b>",
                escaped,
                flags=re.IGNORECASE,
            )
    return escaped


def _link(label: str, url: str) -> str:
    return f'<link href="{escape(url, quote=True)}" color="#0000ee">{escape(label)}</link>'


def _section(
    story: list[Flowable], heading: str, styles: dict[str, ParagraphStyle]
) -> None:
    story.append(Paragraph(escape(heading.upper()), styles["section"]))
    story.append(
        HRFlowable(
            width="100%",
            thickness=0.45,
            color=RULE_COLOR,
            spaceBefore=0,
            spaceAfter=3,
        )
    )


def _contact_line(resume: Resume) -> str:
    contact = resume.personal_info.contact
    parts: list[str] = []
    if contact.phone:
        parts.append(escape(contact.phone))
    for label, value in (
        ("email", contact.email),
        ("Website", contact.website),
        ("LinkedIn", contact.linkedin),
        ("GitHub", contact.github),
    ):
        if value:
            rendered = _link(value if label == "email" else label, f"mailto:{value}" if label == "email" else value)
            parts.append(rendered)
    return " &nbsp; - &nbsp; ".join(parts)


def _two_column_row(
    left: str,
    right: str,
    width: float,
    left_style: ParagraphStyle,
    right_style: ParagraphStyle,
) -> Table:
    table = Table(
        [[Paragraph(left, left_style), Paragraph(right, right_style)]],
        colWidths=[width * 0.69, width * 0.31],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def _render_experience(
    story: list[Flowable],
    experience: Experience,
    width: float,
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(Paragraph(escape(experience.position), styles["position"]))
    company_line = escape(experience.company)
    if experience.location:
        company_line += f" &mdash; {escape(experience.location)}"
    end_date = escape(experience.end_date or "Present")
    dates = f"{escape(experience.start_date)} - {end_date}"
    story.append(_two_column_row(company_line, dates, width, styles["meta"], styles["meta_right"]))
    for item in experience.responsibilities:
        story.append(
            Paragraph(
                _bold_metrics(item.text, item.metrics),
                styles["bullet"],
                bulletText="•",
            )
        )


def _render_education(
    story: list[Flowable],
    education: Education,
    width: float,
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(
        _two_column_row(
            escape(education.institution),
            escape(education.location or ""),
            width,
            styles["education_left"],
            styles["education_right"],
        )
    )
    degree = escape(education.degree)
    if education.field:
        degree += f" in {escape(education.field)}"
    story.append(
        _two_column_row(
            f"<i>{degree}</i>",
            f"<i>{escape(education.start_date)} - {escape(education.end_date or 'Present')}</i>",
            width,
            styles["meta"],
            styles["meta_right"],
        )
    )


def _render_project(
    story: list[Flowable], project: Project, styles: dict[str, ParagraphStyle]
) -> None:
    text = f"<b>{escape(project.name)}:</b> {escape(project.description)}"
    links = []
    if project.links.github:
        links.append(_link("GitHub", project.links.github))
    if project.links.live:
        links.append(_link("Live", project.links.live))
    if links:
        text += " &nbsp; " + " | ".join(links)
    story.append(Paragraph(text, styles["bullet"], bulletText="•"))


def _render_summary(
    story: list[Flowable], resume: Resume, styles: dict[str, ParagraphStyle]
) -> None:
    _section(story, "Professional Summary", styles)
    story.append(Paragraph(escape(resume.summary), styles["body"]))


def build_pdf(resume: Resume, output_path: str | Path) -> None:
    output = Path(output_path)
    page_size = PAGE_SIZES[resume.settings.page_size]
    buffer = BytesIO()
    rendered_pages: set[int] = set()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=page_size,
        leftMargin=0.47 * inch,
        rightMargin=0.47 * inch,
        topMargin=0.24 * inch,
        bottomMargin=0.28 * inch,
        title=f"{resume.personal_info.name} - Resume",
        author=resume.personal_info.name,
    )
    styles = _styles()
    story = [
        Paragraph(escape(resume.personal_info.name), styles["name"]),
        Paragraph(_contact_line(resume), styles["contact"]),
    ]
    section_renderers: dict[str, Callable[[], None]] = {
        "summary": lambda: _render_summary(story, resume, styles),
        "professional_summary": lambda: _render_summary(story, resume, styles),
        "skills": lambda: _render_skills(story, resume, styles),
        "technical_skills": lambda: _render_skills(story, resume, styles),
        "experience": lambda: _render_experience_section(story, resume, doc.width, styles),
        "work_experience": lambda: _render_experience_section(story, resume, doc.width, styles),
        "education": lambda: _render_education_section(story, resume, doc.width, styles),
        "projects": lambda: _render_projects_section(story, resume, styles),
    }
    for section_name in resume.settings.section_order:
        section_renderers[section_name]()

    def track_page(canvas, _document) -> None:
        rendered_pages.add(canvas.getPageNumber())

    doc.build(story, onFirstPage=track_page, onLaterPages=track_page)
    if resume.settings.single_page and len(rendered_pages) > 1:
        raise ValueError(
            f"Resume content needs {len(rendered_pages)} pages, but settings.single_page is true. "
            "Reduce the content or set single_page to false."
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(buffer.getvalue())


def _render_skills(
    story: list[Flowable], resume: Resume, styles: dict[str, ParagraphStyle]
) -> None:
    _section(story, "Technical Skills", styles)
    for group in resume.skills:
        items = ", ".join(escape(item) for item in group.items)
        story.append(Paragraph(f"<b>{escape(group.category)}:</b> {items}", styles["body"]))


def _render_experience_section(
    story: list[Flowable],
    resume: Resume,
    width: float,
    styles: dict[str, ParagraphStyle],
) -> None:
    _section(story, "Work Experience", styles)
    for experience in resume.experience:
        _render_experience(story, experience, width, styles)


def _render_education_section(
    story: list[Flowable],
    resume: Resume,
    width: float,
    styles: dict[str, ParagraphStyle],
) -> None:
    _section(story, "Education", styles)
    for education in resume.education:
        _render_education(story, education, width, styles)


def _render_projects_section(
    story: list[Flowable], resume: Resume, styles: dict[str, ParagraphStyle]
) -> None:
    _section(story, "Projects", styles)
    for project in resume.projects:
        _render_project(story, project, styles)
