from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data" / "placement_dataset.csv"

MODEL_DIR = PROJECT_ROOT / "models"
BRANCH_MODEL_DIR = MODEL_DIR / "branch_models"

METRICS_PATH = MODEL_DIR / "metrics.json"
BRANCH_METRICS_PATH = MODEL_DIR / "branch_model_metrics.json"

TARGET_COLUMN = "placement_status"
BRANCH_COLUMN = "branch"


BRANCH_FEATURES = {
    "CSE": [
        "age",
        "gender",
        "cgpa",
        "college_tier",
        "internships_count",
        "projects_count",
        "certifications_count",
        "coding_skill_score",
        "aptitude_score",
        "communication_skill_score",
        "logical_reasoning_score",
        "hackathons_participated",
        "github_repos",
        "linkedin_connections",
        "mock_interview_score",
        "attendance_percentage",
        "backlogs",
        "extracurricular_score",
        "leadership_score",
        "volunteer_experience",
        "sleep_hours",
        "study_hours_per_day",
    ],
    "IT": [
        "age",
        "gender",
        "cgpa",
        "college_tier",
        "internships_count",
        "projects_count",
        "certifications_count",
        "coding_skill_score",
        "aptitude_score",
        "communication_skill_score",
        "logical_reasoning_score",
        "hackathons_participated",
        "github_repos",
        "linkedin_connections",
        "mock_interview_score",
        "attendance_percentage",
        "backlogs",
        "extracurricular_score",
        "leadership_score",
        "volunteer_experience",
        "sleep_hours",
        "study_hours_per_day",
    ],
    "ECE": [
        "age",
        "gender",
        "cgpa",
        "college_tier",
        "internships_count",
        "projects_count",
        "certifications_count",
        "coding_skill_score",
        "aptitude_score",
        "communication_skill_score",
        "logical_reasoning_score",
        "hackathons_participated",
        "mock_interview_score",
        "attendance_percentage",
        "backlogs",
        "extracurricular_score",
        "leadership_score",
        "volunteer_experience",
        "sleep_hours",
        "study_hours_per_day",
    ],
    "EEE": [
        "age",
        "gender",
        "cgpa",
        "college_tier",
        "internships_count",
        "projects_count",
        "certifications_count",
        "coding_skill_score",
        "aptitude_score",
        "communication_skill_score",
        "logical_reasoning_score",
        "hackathons_participated",
        "mock_interview_score",
        "attendance_percentage",
        "backlogs",
        "extracurricular_score",
        "leadership_score",
        "volunteer_experience",
        "sleep_hours",
        "study_hours_per_day",
    ],
    "Mechanical": [
        "age",
        "gender",
        "cgpa",
        "college_tier",
        "internships_count",
        "projects_count",
        "certifications_count",
        "aptitude_score",
        "communication_skill_score",
        "logical_reasoning_score",
        "mock_interview_score",
        "attendance_percentage",
        "backlogs",
        "extracurricular_score",
        "leadership_score",
        "volunteer_experience",
        "sleep_hours",
        "study_hours_per_day",
    ],
    "Civil": [
        "age",
        "gender",
        "cgpa",
        "college_tier",
        "internships_count",
        "projects_count",
        "certifications_count",
        "aptitude_score",
        "communication_skill_score",
        "logical_reasoning_score",
        "mock_interview_score",
        "attendance_percentage",
        "backlogs",
        "extracurricular_score",
        "leadership_score",
        "volunteer_experience",
        "sleep_hours",
        "study_hours_per_day",
    ],
}


def get_branch_model_path(branch: str) -> Path:
    normalized_branch = branch.lower().replace(" ", "_")
    return BRANCH_MODEL_DIR / f"{normalized_branch}_model.joblib"


def get_numeric_features(branch: str) -> list[str]:
    categorical = get_categorical_features(branch)

    return [
        feature
        for feature in BRANCH_FEATURES[branch]
        if feature not in categorical
    ]


def get_categorical_features(branch: str) -> list[str]:
    all_categorical = {
        "gender",
        "college_tier",
        "volunteer_experience",
    }

    return [
        feature
        for feature in BRANCH_FEATURES[branch]
        if feature in all_categorical
    ]