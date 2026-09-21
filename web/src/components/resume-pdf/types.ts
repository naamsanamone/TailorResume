/**
 * TailorResume — Data mapper
 * Maps our ResumeSection[] format to OpenResume's Resume type
 */

// Our section format (from backend)
export interface TailorSection {
  type: string;
  name?: string;
  fullName?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
  headline?: string;
  text?: string;
  categories?: Record<string, string>;
  items?: string[];
  list_items?: string[];
  entries?: any[];
}

// OpenResume-compatible types
export interface ResumeProfile {
  name: string;
  email: string;
  phone: string;
  url: string;
  summary: string;
  location: string;
}

export interface ResumeWorkExperience {
  company: string;
  jobTitle: string;
  date: string;
  descriptions: string[];
}

export interface ResumeEducation {
  school: string;
  degree: string;
  date: string;
  gpa: string;
  descriptions: string[];
}

export interface ResumeProject {
  project: string;
  date: string;
  descriptions: string[];
}

export interface ResumeSkills {
  descriptions: string[];
}

export interface ResumeCustom {
  heading: string;
  descriptions: string[];
}

export interface MappedResume {
  profile: ResumeProfile;
  workExperiences: ResumeWorkExperience[];
  educations: ResumeEducation[];
  projects: ResumeProject[];
  skills: ResumeSkills;
  customs: ResumeCustom[];
}

/**
 * Convert TailorResume sections to OpenResume-compatible format
 */
export function mapSectionsToResume(sections: TailorSection[]): MappedResume {
  const profile: ResumeProfile = {
    name: "",
    email: "",
    phone: "",
    url: "",
    summary: "",
    location: "",
  };

  const workExperiences: ResumeWorkExperience[] = [];
  const educations: ResumeEducation[] = [];
  const projects: ResumeProject[] = [];
  let skillDescriptions: string[] = [];
  const customs: ResumeCustom[] = [];

  for (const sec of sections) {
    if (!sec || typeof sec !== "object") continue;

    switch (sec.type) {
      case "header": {
        profile.name = sec.fullName || "";
        profile.email = sec.email || "";
        profile.phone = sec.phone || "";
        profile.location = sec.location || "";
        // Combine linkedin/github/portfolio into url
        const urls = [sec.linkedin, sec.github, sec.portfolio].filter(Boolean);
        profile.url = urls.join(" | ");
        break;
      }
      case "summary": {
        profile.summary = sec.text || "";
        break;
      }
      case "experience": {
        for (const entry of sec.entries || []) {
          if (!entry || typeof entry !== "object") continue;
          workExperiences.push({
            company: entry.company || "",
            jobTitle: entry.title || entry.name || "",
            date: entry.duration || entry.date || "",
            descriptions: (entry.bullets || []).filter(
              (b: any) => b && String(b).trim()
            ),
          });
        }
        break;
      }
      case "education": {
        for (const entry of sec.entries || []) {
          if (!entry || typeof entry !== "object") continue;
          educations.push({
            school: entry.institution || entry.company || "",
            degree: entry.degree || entry.title || "",
            date: entry.year || entry.duration || entry.date || "",
            gpa: entry.gpa || "",
            descriptions: (entry.bullets || []).filter(
              (b: any) => b && String(b).trim()
            ),
          });
        }
        break;
      }
      case "projects": {
        for (const entry of sec.entries || []) {
          if (!entry || typeof entry !== "object") continue;
          let projectName = entry.title || entry.name || "";
          if (entry.company) {
            projectName += ` | ${entry.company}`;
          }
          projects.push({
            project: projectName,
            date: entry.duration || entry.date || "",
            descriptions: (entry.bullets || []).filter(
              (b: any) => b && String(b).trim()
            ),
          });
        }
        break;
      }
      case "skills": {
        // Convert categories dict to "Category: skill1, skill2" lines
        const cats = sec.categories;
        if (cats && typeof cats === "object") {
          for (const [catName, catVal] of Object.entries(cats)) {
            skillDescriptions.push(`${catName}: ${String(catVal)}`);
          }
        }
        // Also include plain items
        const items = sec.items || sec.list_items || [];
        for (const item of items) {
          if (item && String(item).trim()) {
            skillDescriptions.push(String(item));
          }
        }
        break;
      }
      case "list":
      case "custom": {
        const items = sec.items || sec.list_items || [];
        let descs: string[] = [];
        if (items.length > 0) {
          descs = items.filter((i: any) => i && String(i).trim()).map(String);
        } else if (sec.text) {
          descs = sec.text
            .split("\n")
            .filter((l) => l.trim())
            .map((l) => l.replace(/^[•\-–·*▪►○]\s*/, "").trim());
        }
        if (descs.length > 0) {
          customs.push({
            heading: sec.name || "Additional",
            descriptions: descs,
          });
        }
        break;
      }
    }
  }

  return {
    profile,
    workExperiences,
    educations,
    projects,
    skills: { descriptions: skillDescriptions },
    customs,
  };
}
