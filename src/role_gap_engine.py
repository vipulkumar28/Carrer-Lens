from src.career_engine import get_role_details


def get_priority(gap):
    if gap >= 25:
        return "High"

    if gap >= 10:
        return "Medium"

    if gap > 0:
        return "Low"

    return "Ready"


def calculate_role_skill_gaps(skill_profile, domain, role):
    role_details = get_role_details(domain, role)
    requirements = role_details["technical_requirements"]

    gaps = []

    for skill, required_score in requirements.items():
        current_score = float(skill_profile.get(skill, 0))
        difference = max(required_score - current_score, 0)

        gaps.append(
            {
                "Skill": skill,
                "Current": round(current_score, 1),
                "Required": required_score,
                "Gap": round(difference, 1),
                "Priority": get_priority(difference),
            }
        )

    return sorted(
        gaps,
        key=lambda item: item["Gap"],
        reverse=True,
    )


def calculate_role_experience_gaps(profile, domain, role):
    role_details = get_role_details(domain, role)
    requirements = role_details["experience_requirements"]

    labels = {
        "projects_count": "Relevant Projects",
        "internships_count": "Relevant Internships",
    }

    gaps = []

    for feature, required_value in requirements.items():
        current_value = float(profile.get(feature, 0))
        difference = max(required_value - current_value, 0)

        gaps.append(
            {
                "Area": labels.get(feature, feature),
                "Current": round(current_value, 1),
                "Required": required_value,
                "Gap": round(difference, 1),
                "Priority": get_priority(difference * 20),
            }
        )

    return gaps