ROLE_ACTIONS = {
    "Python": [
        "Complete Python fundamentals: functions, OOP, files, and error handling.",
        "Solve at least 25 practical Python exercises.",
        "Use Python in one portfolio project.",
    ],
    "SQL": [
        "Learn SELECT, WHERE, JOIN, GROUP BY, HAVING, and subqueries.",
        "Solve at least 30 SQL practice problems.",
        "Build a small SQL-based analysis project.",
    ],
    "Excel": [
        "Practice formulas, pivot tables, lookup functions, and charts.",
        "Create an Excel dashboard using a real dataset.",
        "Document the dashboard in your portfolio.",
    ],
    "Statistics": [
        "Study descriptive statistics, probability, distributions, and hypothesis testing.",
        "Apply statistical analysis to a real dataset.",
        "Explain findings in a portfolio case study.",
    ],
    "Machine Learning": [
        "Learn supervised learning, model evaluation, and feature engineering.",
        "Build one end-to-end machine-learning project.",
        "Deploy or document the project clearly.",
    ],
    "Data Visualization": [
        "Learn chart selection and dashboard storytelling.",
        "Create a dashboard using Power BI, Tableau, or Python.",
        "Add the dashboard to your portfolio.",
    ],
    "Power BI / Tableau": [
        "Learn data cleaning, DAX/calculations, and dashboard design.",
        "Build one interactive business dashboard.",
        "Publish screenshots and project notes in your portfolio.",
    ],
    "AutoCAD": [
        "Practice technical drawing and dimensioning.",
        "Create two branch-relevant design drawings.",
        "Add drawings or screenshots to a portfolio.",
    ],
    "SolidWorks": [
        "Model parts, assemblies, and drawings.",
        "Complete one mechanical design project.",
        "Document design decisions and screenshots.",
    ],
    "CAD": [
        "Strengthen 2D/3D modelling and engineering drawing skills.",
        "Create a branch-relevant CAD portfolio project.",
        "Practice interpreting technical drawings.",
    ],
    "Manufacturing Processes": [
        "Study machining, casting, welding, forming, and quality basics.",
        "Document a manufacturing-process case study.",
        "Seek industrial exposure or workshop experience.",
    ],
    "Surveying": [
        "Study levelling, total station basics, and field measurements.",
        "Complete a surveying case study or field exercise.",
        "Document calculations and observations.",
    ],
    "Construction Planning": [
        "Learn work breakdown structures, scheduling, and resource planning.",
        "Create a small construction-plan case study.",
        "Practice MS Project or equivalent scheduling tools.",
    ],
    "Communication": [
        "Practice a 60-second self-introduction.",
        "Explain one project aloud using the STAR method.",
        "Complete two mock interviews.",
    ],
}


def generate_role_roadmap(role_skill_gaps, role):
    roadmap = []

    priority_gaps = [
        gap
        for gap in role_skill_gaps
        if gap["Priority"] in {"High", "Medium"}
    ]

    for gap in priority_gaps[:3]:
        skill = gap["Skill"]

        roadmap.append(
            {
                "Priority": gap["Priority"],
                "Skill": skill,
                "Current": gap["Current"],
                "Required": gap["Required"],
                "Gap": gap["Gap"],
                "Actions": ROLE_ACTIONS.get(
                    skill,
                    [
                        f"Study the fundamentals of {skill}.",
                        f"Complete a practical {skill} exercise.",
                        f"Use {skill} in a portfolio project.",
                    ],
                ),
            }
        )

    if not roadmap:
        roadmap.append(
            {
                "Priority": "Ready",
                "Skill": role,
                "Current": 100,
                "Required": 100,
                "Gap": 0,
                "Actions": [
                    "Maintain the current skill level.",
                    "Build a stronger portfolio project.",
                    "Start applying for relevant internships and entry-level roles.",
                ],
            }
        )

    return roadmap