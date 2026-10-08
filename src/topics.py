"""
T5: Topic extraction (keyword dictionary approach).
Each comment gets a topic tag by counting keyword hits per category.
"""
import re

import pandas as pd

from config import CLEAN_CSV

TOPIC_KEYWORDS = {
    "Teaching": [
        "teach", "explain", "lecture", "padhan", "padhat", "padhai", "samajh", "samjh", "concept",
        "doubt", "slides", "class", "boring", "speed", "tez", "tarika", "style",
    ],
    "Labs/Practicals": ["lab", "practical", "experiment", "computer", "implement", "hands-on", "hands on", "system"],
    "Exams/Evaluation": [
        "exam", "paper", "marks", "marking", "evaluation", "assignment", "deadline", "question", "pattern",
    ],
    "Course Content": ["syllabus", "content", "notes", "study material", "course", "topics", "outdated", "placement"],
    "Behaviour/Support": [
        "rude", "friendly", "approachable", "support", "respect", "behaviour", "strict", "late",
        "motivat", "help", "scared",
    ],
}


def get_topic(text: str) -> str:
    text = str(text).lower()
    scores = {t: sum(len(re.findall(re.escape(k), text)) for k in kws) for t, kws in TOPIC_KEYWORDS.items()}
    best, score = max(scores.items(), key=lambda kv: kv[1])
    return best if score > 0 else "Other"


def add_topics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Lab / exam / content keywords are specific -> check them on the raw comment first
    df["topic"] = df["comment"].apply(get_topic)
    return df


if __name__ == "__main__":
    d = add_topics(pd.read_csv(CLEAN_CSV))
    print(d["topic"].value_counts())
    d.to_csv(CLEAN_CSV, index=False)
    print("Topic column saved.")
