import json

from src.config import PROJECT_ROOT


CATALOG_PATH = PROJECT_ROOT / "data" / "career_catalog.json"


def load_career_catalog():
    with CATALOG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_career_domains():
    return list(load_career_catalog().keys())

def get_roles_for_domain(domain):
    catalog = load_career_catalog()

    if domain not in catalog:
        return []

    return list(catalog[domain].keys())

def get_role_details(domain, role):
    catalog = load_career_catalog()

    if domain not in catalog:
        raise ValueError(f"Unknown career domain: {domain}")

    if role not in catalog[domain]:
        raise ValueError(
            f"Unknown role '{role}' in domain '{domain}'."
        )

    return catalog[domain][role]


def get_academic_compatibility(branch, recommended_backgrounds):
    if branch in recommended_backgrounds:
        return {
            "label": "Strong",
            "score": 100,
            "message": (
                f"{branch} is a recommended academic background "
                "for this role."
            ),
        }

    transferable_backgrounds = {
        "CSE",
        "IT",
        "ECE",
        "EEE",
        "Mechanical",
        "Civil",
    }

    if branch in transferable_backgrounds:
        return {
            "label": "Transferable",
            "score": 60,
            "message": (
                f"{branch} is not the primary background for this role, "
                "but the career path can be explored through skill building."
            ),
        }

    return {
        "label": "Limited",
        "score": 30,
        "message": (
            "This role may require substantial additional skill building "
            "or a different academic foundation."
        ),
    }


def calculate_technical_skill_match(skill_profile, requirements):
    if not requirements:
        return 0.0

    total_score = 0.0

    for skill, required_score in requirements.items():
        current_score = float(skill_profile.get(skill, 0))
        match_ratio = min(current_score / required_score, 1.0)
        total_score += match_ratio * 100

    return round(total_score / len(requirements), 1)


def calculate_experience_match(profile, requirements):
    if not requirements:
        return 100.0

    total_score = 0.0

    for feature, required_value in requirements.items():
        current_value = float(profile.get(feature, 0))
        required_value = float(required_value)

        if required_value <= 0:
            match_ratio = 1.0
        else:
            match_ratio = min(
                current_value / required_value,
                1.0,
            )

        total_score += match_ratio * 100

    return round(total_score / len(requirements), 1)

def calculate_role_match(profile, skill_profile, domain, role):
    role_details = get_role_details(domain, role)

    compatibility = get_academic_compatibility(
        profile["branch"],
        role_details["recommended_backgrounds"],
    )

    technical_match = calculate_technical_skill_match(
        skill_profile,
        role_details["technical_requirements"],
    )

    experience_match = calculate_experience_match(
        profile,
        role_details["experience_requirements"],
    )

    overall_readiness = (
        (
            float(profile["cgpa"]) / 10
            + float(profile["aptitude_score"]) / 100
            + float(profile["communication_skill_score"]) / 100
        )
        / 3
        * 100
    )

    overall_score = (
        compatibility["score"] * 0.20
        + technical_match * 0.45
        + experience_match * 0.20
        + overall_readiness * 0.15
    )

    return {
        "role": role,
        "domain": domain,
        "overall_match": round(overall_score, 1),
        "academic_compatibility": compatibility,
        "technical_match": technical_match,
        "experience_match": experience_match,
        "overall_readiness": round(overall_readiness, 1),
    }


def recommend_roles(profile, skill_profile, top_n=5):
    catalog = load_career_catalog()
    role_matches = []

    for domain, roles in catalog.items():
        for role in roles:
            match = calculate_role_match(
                profile,
                skill_profile,
                domain,
                role,
            )
            role_matches.append(match)

    return sorted(
        role_matches,
        key=lambda item: item["overall_match"],
        reverse=True,
    )[:top_n]