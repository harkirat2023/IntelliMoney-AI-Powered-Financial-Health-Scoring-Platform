"""Train TF-IDF + Logistic Regression model for expense categorization."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "ml" / "data" / "expenses.csv"
MODEL_PATH = ROOT / "backend" / "app" / "ml" / "expense_classifier.joblib"


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    lowercase=True,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(C=10.0, max_iter=1000, random_state=42),
            ),
        ]
    )


def train() -> None:
    data = pd.read_csv(DATA_PATH)
    x_train, x_test, y_train, y_test = train_test_split(
        data["description"],
        data["category"],
        test_size=0.2,
        random_state=42,
        stratify=data["category"],
    )

    eval_pipeline = build_pipeline()
    eval_pipeline.fit(x_train, y_train)
    predictions = eval_pipeline.predict(x_test)
    print("--- Holdout Evaluation Report ---")
    print(classification_report(y_test, predictions, zero_division=0))

    # Fit final pipeline on all available data for production deployment
    final_pipeline = build_pipeline()
    final_pipeline.fit(data["description"], data["category"])

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_pipeline, MODEL_PATH)
    print(f"Saved optimized model to {MODEL_PATH}")


if __name__ == "__main__":
    train()
