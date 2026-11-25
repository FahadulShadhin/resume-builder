from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


SectionName = Literal[
    "summary",
    "professional_summary",
    "skills",
    "technical_skills",
    "experience",
    "work_experience",
    "education",
    "projects",
]


class ResumeModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Contact(ResumeModel):
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    linkedin: str | None = None
    github: str | None = None


class PersonalInfo(ResumeModel):
    name: str
    title: str | None = None
    contact: Contact = Field(default_factory=Contact)


class SkillGroup(ResumeModel):
    category: str
    items: list[str]


class Responsibility(ResumeModel):
    text: str
    metrics: list[str] = Field(default_factory=list)
    client: str | None = None


class Experience(ResumeModel):
    company: str
    employment_type: str | None = None
    position: str
    location: str | None = None
    start_date: str
    end_date: str | None = None
    responsibilities: list[Responsibility]


class Education(ResumeModel):
    institution: str
    degree: str
    field: str | None = None
    location: str | None = None
    start_date: str
    end_date: str | None = None


class ProjectLinks(ResumeModel):
    github: str | None = None
    live: str | None = None


class Project(ResumeModel):
    name: str
    description: str
    links: ProjectLinks = Field(default_factory=ProjectLinks)


class ResumeSettings(ResumeModel):
    page_size: Literal["LETTER", "A4"] = "LETTER"
    single_page: bool = True
    section_order: list[SectionName] = Field(
        default_factory=lambda: [
            "summary",
            "skills",
            "experience",
            "education",
            "projects",
        ]
    )


class Resume(ResumeModel):
    personal_info: PersonalInfo
    summary: str = Field(
        validation_alias=AliasChoices("summary", "professional_summary")
    )
    skills: list[SkillGroup] = Field(
        default_factory=list,
        validation_alias=AliasChoices("skills", "technical_skills"),
    )
    experience: list[Experience] = Field(
        default_factory=list,
        validation_alias=AliasChoices("experience", "work_experience"),
    )
    education: list[Education] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    settings: ResumeSettings = Field(
        default_factory=ResumeSettings,
        validation_alias=AliasChoices("settings", "layout_settings"),
    )
