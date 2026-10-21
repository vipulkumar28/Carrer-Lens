GENERAL_READINESS_THRESHOLDS = {
    "cgpa": ("Academic Performance", 7.0),
    "attendance_percentage": ("Attendance", 75.0),
    "aptitude_score": ("Aptitude", 70.0),
    "communication_skill_score": ("Communication", 75.0),
    "logical_reasoning_score": ("Logical Reasoning", 70.0),
    "mock_interview_score": ("Interview Readiness", 75.0),
    "projects_count": ("Practical Experience", 3.0),
    "internships_count": ("Industry Exposure", 1.0),
}


def get_priority(gap, scale=1.0):
    adjusted_gap = gap * scale

    if adjusted_gap >= 20:
        return "High"

    if adjusted_gap >= 8:
        return "Medium"

    if adjusted_gap > 0:
        return "Low"

    return "Ready"


def calculate_overall_readiness_gaps(profile):
    gaps = []

    for feature, (label, required_value) in GENERAL_READINESS_THRESHOLDS.items():
        current_value = float(profile[feature])
        difference = max(required_value - current_value, 0)

        if feature == "cgpa":
            priority = get_priority(difference, scale=10)
        elif feature in {"projects_count", "internships_count"}:
            priority = get_priority(difference, scale=20)
        else:
            priority = get_priority(difference)

        gaps.append(
            {
                "Area": label,
                "Current": round(current_value, 1),
                "Target": required_value,
                "Gap": round(difference, 1),
                "Priority": priority,
            }
        )

    return sorted(
        gaps,
        key=lambda item: (
            item["Priority"] != "High",
            item["Priority"] != "Medium",
            item["Priority"] != "Low",
            -item["Gap"],
        ),
    )


def calculate_overall_readiness_score(profile):
    academic = (
        (float(profile["cgpa"]) / 10) * 70
        + float(profile["attendance_percentage"]) * 0.20
        + max(0, 100 - float(profile["backlogs"]) * 15) * 0.10
    )

    aptitude = (
        float(profile["aptitude_score"]) * 0.50
        + float(profile["logical_reasoning_score"]) * 0.50
    )

    communication = (
        float(profile["communication_skill_score"]) * 0.60
        + float(profile["mock_interview_score"]) * 0.40
    )

    experience = (
        min(float(profile["projects_count"]) / 3, 1) * 45
        + min(float(profile["internships_count"]) / 1, 1) * 35
        + min(float(profile["certifications_count"]) / 3, 1) * 20
    )

    overall = (
        academic * 0.30
        + aptitude * 0.25
        + communication * 0.20
        + experience * 0.25
    )

    return {
        "Academic": round(min(academic, 100), 1),
        "Aptitude & Reasoning": round(min(aptitude, 100), 1),
        "Communication & Interview": round(min(communication, 100), 1),
        "Experience": round(min(experience, 100), 1),
        "Overall": round(min(overall, 100), 1),
    }