import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
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
    CATEGORICAL_FEATURES,
    DATA_PATH,
    FEATURE_COLUMNS,
    METRICS_PATH,
    MODEL_DIR,
    MODEL_PATH,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
)


def build_preprocessor():
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
                "one_hot_encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def build_models():
    return {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }


def evaluate_model(model, x_test, y_test):
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


def main():
    print("Loading dataset...")
    data = pd.read_csv(DATA_PATH)

    data[TARGET_COLUMN] = data[TARGET_COLUMN].map(
        {
            "Not Placed": 0,
            "Placed": 1,
        }
    )

    data = data.dropna(subset=[TARGET_COLUMN])

    x = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN]

    print(f"Rows: {len(data)}")
    print(f"Features: {len(FEATURE_COLUMNS)}")

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    results = {}
    trained_models = {}

    for model_name, classifier in build_models().items():
        print(f"\nTraining {model_name}...")

        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor()),
                ("classifier", classifier),
            ]
        )

        pipeline.fit(x_train, y_train)

        metrics = evaluate_model(pipeline, x_test, y_test)
        results[model_name] = metrics
        trained_models[model_name] = pipeline

        print(metrics["classification_report"])

    best_model_name = max(
        results,
        key=lambda name: results[name]["f1_score"],
    )

    best_model = trained_models[best_model_name]

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)

    output_metrics = {
        "best_model": best_model_name,
        "dataset_rows": int(len(data)),
        "feature_count": len(FEATURE_COLUMNS),
        "models": results,
    }

    with METRICS_PATH.open("w", encoding="utf-8") as file:
        json.dump(output_metrics, file, indent=4)

    print(f"\nBest model: {best_model_name}")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")


if __name__ == "__main__":
    main()