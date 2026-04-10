export interface PersonalInfo {
  name: string
  email: string
  phone: string
  location: string
  linkedin: string
  github: string
  website: string
  summary: string
}

export interface EducationEntry {
  institution: string
  degree: string
  field: string
  start_date: string
  end_date: string
  gpa: string
  description: string
}

export interface WorkEntry {
  company: string
  title: string
  start_date: string
  end_date: string
  location: string
  bullets: string[]
}

export interface ProjectEntry {
  name: string
  description: string
  technologies: string[]
  url: string
  bullets: string[]
}

export interface SkillsMap {
  languages: string[]
  frameworks: string[]
  tools: string[]
  other: string[]
}

export interface ParsedResume {
  personal: PersonalInfo
  education: EducationEntry[]
  work_experience: WorkEntry[]
  projects: ProjectEntry[]
  skills: SkillsMap
}

export interface PaperParsed {
  title: string
  authors: string[]
  abstract: string
  venue: string
  year: string
  doi: string
  keywords: string[]
  key_contributions: string[]
  methodology_summary: string
  results_summary: string
}
