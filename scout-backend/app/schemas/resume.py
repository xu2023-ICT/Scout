from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PersonalInfo(BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    summary: str = ""


class EducationEntry(BaseModel):
    institution: str
    degree: str
    field: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""
    description: str = ""


class WorkEntry(BaseModel):
    company: str
    title: str
    start_date: str = ""
    end_date: str = ""
    location: str = ""
    bullets: list[str] = []


class ProjectEntry(BaseModel):
    name: str
    description: str = ""
    technologies: list[str] = []
    url: str = ""
    bullets: list[str] = []


class SkillsMap(BaseModel):
    languages: list[str] = []
    frameworks: list[str] = []
    tools: list[str] = []
    other: list[str] = []


class ParsedResume(BaseModel):
    personal: PersonalInfo
    education: list[EducationEntry] = []
    work_experience: list[WorkEntry] = []
    projects: list[ProjectEntry] = []
    skills: SkillsMap = SkillsMap()


class PaperParsed(BaseModel):
    title: str
    authors: list[str] = []
    abstract: str = ""
    venue: str = ""
    year: str = ""
    doi: str = ""
    keywords: list[str] = []
    key_contributions: list[str] = []
    methodology_summary: str = ""
    results_summary: str = ""


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    parsed_data: ParsedResume
    github_url: str | None
    confirmed: bool
    created_at: datetime
    paper: PaperParsed | None = None


class ResumeUpdate(BaseModel):
    parsed_data: ParsedResume
    github_url: str | None = None
