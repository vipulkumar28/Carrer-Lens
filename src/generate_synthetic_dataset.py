from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
ROW_COUNT = 5000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_PATH = DATA_DIR / "placement_dataset.csv"


def clip_round(values, minimum, maximum, decimals=2):
    return np.round(
        np.clip(values, minimum, maximum),
        decimals,
    )


def sigmoid(values):
    return 1 / (1 + np.exp(-values))


def main():
    rng = np.random.default_rng(RANDOM_SEED)
    n = ROW_COUNT

    student_id = np.arange(1, n + 1)

    branches = rng.choice(
        ["CSE", "IT", "ECE", "EEE", "Mechanical", "Civil"],
        size=n,
        p=[0.28, 0.15, 0.18, 0.12, 0.15, 0.12],
    )

    gender = rng.choice(
        ["Male", "Female"],
        size=n,
        p=[0.58, 0.42],
    )

    college_tier = rng.choice(
        ["Tier 1", "Tier 2", "Tier 3"],
        size=n,
        p=[0.22, 0.50, 0.28],
    )

    volunteer_experience = rng.choice(
        ["Yes", "No"],
        size=n,
        p=[0.42, 0.58],
    )

    age = rng.integers(18, 25, size=n)

    tier_bonus = np.select(
        [
            college_tier == "Tier 1",
            college_tier == "Tier 2",
            college_tier == "Tier 3",
        ],
        [0.45, 0.10, -0.35],
    )

    branch_tech_bonus = np.select(
        [
            np.isin(branches, ["CSE", "IT"]),
            np.isin(branches, ["ECE", "EEE"]),
            np.isin(branches, ["Mechanical", "Civil"]),
        ],
        [4.0, 1.5, -1.5],
    )

    academic_ability = rng.normal(0, 1, size=n)

    cgpa = clip_round(
        7.30
        + academic_ability * 0.95
        + tier_bonus * 0.28
        + rng.normal(0, 0.42, size=n),
        4.5,
        10.0,
    )

    aptitude_score = clip_round(
        65
        + academic_ability * 9
        + tier_bonus * 3
        + rng.normal(0, 10, size=n),
        20,
        100,
    )

    logical_reasoning_score = clip_round(
        66
        + academic_ability * 8
        + tier_bonus * 2
        + rng.normal(0, 10, size=n),
        20,
        100,
    )

    coding_skill_score = clip_round(
        62
        + academic_ability * 8
        + branch_tech_bonus
        + rng.normal(0, 13, size=n),
        20,
        100,
    )

    communication_skill_score = clip_round(
        67
        + academic_ability * 4
        + (volunteer_experience == "Yes") * 5
        + rng.normal(0, 11, size=n),
        20,
        100,
    )

    leadership_score = clip_round(
        53
        + (volunteer_experience == "Yes") * 10
        + rng.normal(0, 15, size=n),
        0,
        100,
    )

    extracurricular_score = clip_round(
        58
        + (volunteer_experience == "Yes") * 9
        + rng.normal(0, 16, size=n),
        0,
        100,
    )

    attendance_percentage = clip_round(
        84
        + academic_ability * 3
        + rng.normal(0, 7, size=n),
        50,
        100,
    )

    study_hours_per_day = clip_round(
        3.4
        + academic_ability * 0.65
        + rng.normal(0, 1.2, size=n),
        0.5,
        10.0,
        decimals=1,
    )

    sleep_hours = clip_round(
        7.0
        - np.abs(study_hours_per_day - 3.5) * 0.15
        + rng.normal(0, 0.8, size=n),
        3.0,
        10.0,
        decimals=1,
    )

    backlogs_probability = sigmoid(
        -0.8
        - academic_ability * 1.1
        - (attendance_percentage - 75) * 0.03
    )

    backlogs = rng.binomial(
        4,
        np.clip(backlogs_probability, 0.02, 0.55),
    )

    internships_count = np.clip(
        rng.poisson(
            0.8
            + (cgpa >= 7.5) * 0.55
            + (college_tier == "Tier 1") * 0.35
            + (college_tier == "Tier 2") * 0.12
        ),
        0,
        6,
    )

    projects_count = np.clip(
        rng.poisson(
            1.7
            + (coding_skill_score >= 70) * 0.8
            + (study_hours_per_day >= 4) * 0.35
            + (branches == "CSE") * 0.35
            + (branches == "IT") * 0.20
        ),
        0,
        10,
    )

    certifications_count = np.clip(
        rng.poisson(
            1.2
            + (study_hours_per_day >= 4) * 0.45
            + (college_tier == "Tier 1") * 0.20
        ),
        0,
        8,
    )

    hackathons_participated = np.clip(
        rng.poisson(
            0.35
            + np.isin(branches, ["CSE", "IT"]) * 0.8
            + np.isin(branches, ["ECE", "EEE"]) * 0.25
        ),
        0,
        7,
    )

    github_repos = np.clip(
        rng.poisson(
            1.0
            + np.isin(branches, ["CSE", "IT"]) * 2.0
            + np.isin(branches, ["ECE", "EEE"]) * 0.55
            + (projects_count >= 3) * 0.55
        ),
        0,
        15,
    )

    linkedin_connections = np.clip(
        (
            170
            + internships_count * 75
            + projects_count * 25
            + (volunteer_experience == "Yes") * 55
            + rng.normal(0, 135, size=n)
        ).astype(int),
        50,
        999,
    )

    mock_interview_score = clip_round(
        46
        + communication_skill_score * 0.30
        + logical_reasoning_score * 0.20
        + internships_count * 2.8
        + projects_count * 1.4
        - backlogs * 1.8
        + rng.normal(0, 7, size=n),
        20,
        100,
    )

    tier_effect = np.select(
        [
            college_tier == "Tier 1",
            college_tier == "Tier 2",
            college_tier == "Tier 3",
        ],
        [0.70, 0.20, -0.55],
    )

    branch_effect = np.select(
        [
            np.isin(branches, ["CSE", "IT"]),
            np.isin(branches, ["ECE", "EEE"]),
            np.isin(branches, ["Mechanical", "Civil"]),
        ],
        [0.25, 0.05, -0.20],
    )

    placement_logit = (
        -0.95
        + (cgpa - 7.0) * 0.95
        + (aptitude_score - 60) * 0.025
        + (communication_skill_score - 60) * 0.020
        + (logical_reasoning_score - 60) * 0.020
        + (mock_interview_score - 60) * 0.050
        + internships_count * 0.50
        + projects_count * 0.22
        + certifications_count * 0.08
        + (attendance_percentage - 75) * 0.024
        - backlogs * 0.60
        + leadership_score * 0.006
        + extracurricular_score * 0.003
        + (volunteer_experience == "Yes") * 0.18
        + tier_effect
        + branch_effect
        + rng.normal(0, 0.55, size=n)
    )

    placement_probability = sigmoid(placement_logit)

    placed = rng.binomial(
        1,
        np.clip(placement_probability, 0.03, 0.97),
    )

    placement_status = np.where(
        placed == 1,
        "Placed",
        "Not Placed",
    )

    branch_salary_bonus = np.select(
        [
            np.isin(branches, ["CSE", "IT"]),
            np.isin(branches, ["ECE", "EEE"]),
            np.isin(branches, ["Mechanical", "Civil"]),
        ],
        [1.5, 0.5, 0.0],
    )

    tier_salary_bonus = np.select(
        [
            college_tier == "Tier 1",
            college_tier == "Tier 2",
            college_tier == "Tier 3",
        ],
        [1.6, 0.6, 0.0],
    )

    salary_package_lpa = np.where(
        placed == 1,
        clip_round(
            4.0
            + cgpa * 0.68
            + internships_count * 0.42
            + projects_count * 0.20
            + mock_interview_score * 0.025
            + branch_salary_bonus
            + tier_salary_bonus
            + rng.normal(0, 0.8, size=n),
            3.0,
            25.0,
        ),
        0.0,
    )

    data = pd.DataFrame(
        {
            "student_id": student_id,
            "age": age,
            "gender": gender,
            "cgpa": cgpa,
            "branch": branches,
            "college_tier": college_tier,
            "internships_count": internships_count,
            "projects_count": projects_count,
            "certifications_count": certifications_count,
            "coding_skill_score": coding_skill_score,
            "aptitude_score": aptitude_score,
            "communication_skill_score": communication_skill_score,
            "logical_reasoning_score": logical_reasoning_score,
            "hackathons_participated": hackathons_participated,
            "github_repos": github_repos,
            "linkedin_connections": linkedin_connections,
            "mock_interview_score": mock_interview_score,
            "attendance_percentage": attendance_percentage,
            "backlogs": backlogs,
            "extracurricular_score": extracurricular_score,
            "leadership_score": leadership_score,
            "volunteer_experience": volunteer_experience,
            "sleep_hours": sleep_hours,
            "study_hours_per_day": study_hours_per_day,
            "placement_status": placement_status,
            "salary_package_lpa": salary_package_lpa,
        }
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    data.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(f"Dataset saved to: {OUTPUT_PATH}")
    print(f"Rows: {len(data)}")
    print(f"Columns: {len(data.columns)}")

    print("\nPlacement distribution:")
    print(data["placement_status"].value_counts())
    print(
        data["placement_status"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    print("\nAverage profile by placement status:")
    summary_columns = [
        "cgpa",
        "internships_count",
        "projects_count",
        "aptitude_score",
        "communication_skill_score",
        "logical_reasoning_score",
        "mock_interview_score",
        "attendance_percentage",
        "backlogs",
    ]

    print(
        data.groupby("placement_status")[summary_columns]
        .mean()
        .round(2)
    )


if __name__ == "__main__":
    main()