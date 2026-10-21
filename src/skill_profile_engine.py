DOMAIN_SKILLS = {
    "Data & AI": [
        "Python",
        "SQL",
        "Excel",
        "Statistics",
        "Machine Learning",
        "Data Visualization",
        "Power BI / Tableau",
        "Git / GitHub",
    ],
    "Software & IT": [
        "Python",
        "Java",
        "JavaScript",
        "Data Structures and Algorithms",
        "SQL",
        "Git / GitHub",
        "Backend Development",
        "Frontend Development",
        "Cloud Fundamentals",
    ],
    "Cybersecurity": [
        "Networking",
        "Linux",
        "Python",
        "Web Security",
        "Security Tools",
        "Cryptography Basics",
        "Incident Response",
        "Cloud Security",
    ],
    "Electronics & Embedded": [
        "C / C++",
        "Embedded Systems",
        "Microcontrollers",
        "Digital Electronics",
        "IoT",
        "PCB Design",
        "MATLAB",
        "Circuit Design",
    ],
    "Mechanical Engineering": [
        "AutoCAD",
        "SolidWorks",
        "CAD",
        "Manufacturing Processes",
        "Thermodynamics",
        "Machine Design",
        "Quality Control",
        "Production Planning",
    ],
    "Civil Engineering": [
        "AutoCAD",
        "Revit / BIM",
        "Surveying",
        "Structural Analysis",
        "Estimation and Costing",
        "Construction Planning",
        "Site Safety",
        "Project Scheduling",
    ],
    "Business & Analytics": [
        "Excel",
        "Business Communication",
        "Power BI / Tableau",
        "SQL",
        "Business Analysis",
        "Presentation Skills",
        "Stakeholder Management",
        "Project Coordination",
    ],
    "Design & Creative": [
        "Figma",
        "UI Design",
        "UX Research",
        "Wireframing",
        "Prototyping",
        "Design Systems",
        "Visual Communication",
        "Portfolio Development",
    ],
    "Product & Management": [
        "Product Thinking",
        "Market Research",
        "Data Analysis",
        "Communication",
        "Stakeholder Management",
        "Project Management",
        "Agile / Scrum",
        "Presentation Skills",
    ],
    "Other": [
        "Communication",
        "Problem Solving",
        "Research",
        "Documentation",
        "Presentation Skills",
        "Project Management",
    ],
}


def get_skills_for_domain(domain):
    return DOMAIN_SKILLS.get(domain, DOMAIN_SKILLS["Other"])


def build_skill_profile(domain, values):
    skills = get_skills_for_domain(domain)

    return {
        skill: float(values.get(skill, 0))
        for skill in skills
    }