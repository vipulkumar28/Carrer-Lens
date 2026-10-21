from functools import lru_cache

import joblib
import pandas as pd

from src.config import (
    BRANCH_FEATURES,
    get_branch_model_path,
)


@lru_cache(maxsize=6)
def load_branch_model(branch: str):
    model_path = get_branch_model_path(branch)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Branch model not found for '{branch}'. "
            "Run: python -m src.train_branch_models"
        )

    return joblib.load(model_path)


def build_branch_model_input(profile: dict) -> pd.DataFrame:
    branch = profile["branch"]

    if branch not in BRANCH_FEATURES:
        raise ValueError(
            f"Unsupported branch: {branch}"
        )

    feature_columns = BRANCH_FEATURES[branch]

    missing_features = [
        feature
        for feature in feature_columns
        if feature not in profile
    ]

    if missing_features:
        missing_text = ", ".join(missing_features)

        raise ValueError(
            f"Profile is missing required features: {missing_text}"
        )

    return pd.DataFrame(
        [
            {
                feature: profile[feature]
                for feature in feature_columns
            }
        ]
    )


def predict_placement(profile: dict) -> dict:
    branch = profile["branch"]

    model = load_branch_model(branch)
    model_input = build_branch_model_input(profile)

    prediction = int(model.predict(model_input)[0])
    probability = float(
        model.predict_proba(model_input)[0][1]
    )

    return {
        "prediction": prediction,
        "probability": probability,
        "model_type": "branch_specific",
        "branch_model": branch,
    }