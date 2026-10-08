"""
T4: Sentiment model training + evaluation.
Trains Naive Bayes and Logistic Regression on TF-IDF features, compares with VADER,
saves the best pipeline to models/sentiment_model.pkl and writes plots/metrics to outputs/.
"""
import json

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import CLEAN_CSV, MODEL_PATH, OUT_DIR, RANDOM_STATE

LABELS = ["negative", "neutral", "positive"]


def vader_predict(texts):
    sia = SentimentIntensityAnalyzer()
    preds = []
    for t in texts:
        c = sia.polarity_scores(str(t))["compound"]
        preds.append("positive" if c >= 0.05 else "negative" if c <= -0.05 else "neutral")
    return preds


def main():
    df = pd.read_csv(CLEAN_CSV)
    X, y = df["clean_comment"], df["sentiment"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    print(f"Train: {len(X_train)} | Test: {len(X_test)}")

    models = {
        "Naive Bayes": MultinomialNB(alpha=0.5),
        "Logistic Regression": LogisticRegression(max_iter=1000, C=5, random_state=RANDOM_STATE),
    }

    results, fitted = {}, {}
    for name, clf in models.items():
        pipe = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)), ("clf", clf)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        cv = cross_val_score(pipe, X, y, cv=5, scoring="accuracy").mean()
        results[name] = {
            "accuracy": round(accuracy_score(y_test, pred), 4),
            "f1_macro": round(f1_score(y_test, pred, average="macro"), 4),
            "cv_accuracy": round(cv, 4),
        }
        fitted[name] = (pipe, pred)

    # VADER baseline on raw comments (no training)
    raw_test = df.loc[X_test.index, "comment"]
    v_pred = vader_predict(raw_test)
    results["VADER (baseline)"] = {
        "accuracy": round(accuracy_score(y_test, v_pred), 4),
        "f1_macro": round(f1_score(y_test, v_pred, average="macro"), 4),
        "cv_accuracy": None,
    }

    comp = pd.DataFrame(results).T
    print("\n=== Model comparison ===")
    print(comp)
    comp.to_csv(OUT_DIR / "model_comparison.csv")

    best_name = max(["Naive Bayes", "Logistic Regression"], key=lambda n: results[n]["f1_macro"])
    best_pipe, best_pred = fitted[best_name]
    print(f"\nBest model: {best_name}")
    print(classification_report(y_test, best_pred, labels=LABELS, zero_division=0))

    with open(OUT_DIR / "classification_report.txt", "w") as f:
        f.write(f"Best model: {best_name}\n\n")
        f.write(classification_report(y_test, best_pred, labels=LABELS, zero_division=0))
    with open(OUT_DIR / "metrics.json", "w") as f:
        json.dump({"best_model": best_name, "results": results}, f, indent=2)

    cm = confusion_matrix(y_test, best_pred, labels=LABELS)
    plt.figure(figsize=(5.5, 4.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=LABELS, yticklabels=LABELS)
    plt.title(f"Confusion Matrix - {best_name}")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "confusion_matrix.png", dpi=150)
    plt.close()

    plt.figure(figsize=(7, 4))
    comp["accuracy"].astype(float).plot(kind="bar", color=["#4C72B0", "#55A868", "#C44E52"])
    plt.ylim(0, 1)
    plt.ylabel("Accuracy")
    plt.title("Model comparison (test accuracy)")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "model_comparison.png", dpi=150)
    plt.close()

    # Refit best pipeline on ALL data before saving for the app
    best_pipe.fit(X, y)
    joblib.dump(best_pipe, MODEL_PATH)
    print(f"Saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
