import json
import hashlib
from datetime import datetime
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    BRANCH_COLUMN,
    BRANCH_FEATURES,
    BRANCH_METRICS_PATH,
    BRANCH_MODEL_DIR,
    DATA_PATH,
    TARGET_COLUMN,
    get_branch_model_path,
    get_categorical_features,
    get_numeric_features,
)


RANDOM_STATE = 42
TEST_SIZE = 0.20
MINIMUM_BRANCH_RECORDS = 500
MINIMUM_CLASS_RECORDS = 100


def create_preprocessor(branch: str) -> ColumnTransformer:
    numeric_features = get_numeric_features(branch)
    categorical_features = get_categorical_features(branch)

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )


def create_model(branch: str) -> Pipeline:
    preprocessor = create_preprocessor(branch)

    classifier = RandomForestClassifier(
        n_estimators=250,
        max_depth=14,
        min_samples_split=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def calculate_metrics(model, x_test, y_test) -> dict:
    predictions = model.predict(x_test)

    return {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(
            float(precision_score(y_test, predictions, zero_division=0)),
            4,
        ),
        "recall": round(
            float(recall_score(y_test, predictions, zero_division=0)),
            4,
        ),
        "f1_score": round(
            float(f1_score(y_test, predictions, zero_division=0)),
            4,
        ),
        "classification_report": classification_report(
            y_test,
            predictions,
            target_names=["Not Placed", "Placed"],
            zero_division=0,
        ),
    }


def train_single_branch(data: pd.DataFrame, branch: str) -> dict:
    branch_data = data[data[BRANCH_COLUMN] == branch].copy()

    if len(branch_data) < MINIMUM_BRANCH_RECORDS:
        return {
            "status": "skipped",
            "reason": (
                f"Only {len(branch_data)} rows available. "
                f"Minimum required: {MINIMUM_BRANCH_RECORDS}."
            ),
        }

    target_counts = branch_data[TARGET_COLUMN].value_counts()

    if len(target_counts) < 2:
        return {
            "status": "skipped",
            "reason": "Only one target class exists for this branch.",
        }

    if target_counts.min() < 20:
        return {
            "status": "skipped",
            "reason": (
                "At least one target class has fewer than 20 records."
            ),
        }

    feature_columns = BRANCH_FEATURES[branch]

    x = branch_data[feature_columns]
    y = branch_data[TARGET_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = create_model(branch)
    model.fit(x_train, y_train)

    metrics = calculate_metrics(model, x_test, y_test)

    model_path = get_branch_model_path(branch)
    joblib.dump(model, model_path)

    print("\n" + "=" * 72)
    print(f"BRANCH: {branch}")
    print("=" * 72)
    print(f"Rows: {len(branch_data)}")
    print(f"Features used: {len(feature_columns)}")
    print(f"Placed: {int((y == 1).sum())}")
    print(f"Not Placed: {int((y == 0).sum())}")
    print("\nClassification report:")
    print(metrics["classification_report"])
    print(f"Saved model: {model_path}")

    return {
        "status": "trained",
        "rows": int(len(branch_data)),
        "features": feature_columns,
        "placed_count": int((y == 1).sum()),
        "not_placed_count": int((y == 0).sum()),
        "model_path": str(model_path),
        "metrics": metrics,
    }

def get_file_sha256(file_path):
    hasher = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)

    return hasher.hexdigest()

def main() -> None:
    print("Loading placement dataset...")

    data = pd.read_csv(DATA_PATH)
    dataset_hash = get_file_sha256(DATA_PATH)

    print(f"\nTraining dataset: {DATA_PATH.resolve()}")
    print(f"Dataset SHA-256: {dataset_hash}")
    print(f"Dataset rows: {len(data)}")
    print(f"Training timestamp: {datetime.now().isoformat()}")

    data[TARGET_COLUMN] = data[TARGET_COLUMN].map(
        {
            "Not Placed": 0,
            "Placed": 1,
        }
    )

    data = data.dropna(
        subset=[
            TARGET_COLUMN,
            BRANCH_COLUMN,
        ]
    )

    BRANCH_MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_metrics = {
    "model_type": "branch_specific_random_forest",
    "training_dataset_path": str(DATA_PATH.resolve()),
    "training_dataset_sha256": dataset_hash,
    "training_timestamp": datetime.now().isoformat(),
    "dataset_rows": int(len(data)),
    "dataset_columns": list(data.columns),
    "branches": {},
    }

    print("\nBranch distribution:")
    print(data[BRANCH_COLUMN].value_counts())

    for branch in BRANCH_FEATURES:
        result = train_single_branch(data, branch)
        all_metrics["branches"][branch] = result

    with BRANCH_METRICS_PATH.open(
        "w",
        encoding="utf-8",
    ) as metrics_file:
        json.dump(
            all_metrics,
            metrics_file,
            indent=4,
        )

    print("\n" + "=" * 72)
    print("Branch-specific training completed.")
    print(f"Metrics saved to: {BRANCH_METRICS_PATH}")


if __name__ == "__main__":
    main()