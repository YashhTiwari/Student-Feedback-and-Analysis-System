"""
T3: Text preprocessing.
Steps: lowercase -> remove punctuation/numbers/emojis -> tokenize -> remove stopwords -> light lemmatization.

NOTE: negation words (not, no, nahi, never...) are deliberately KEPT, because
"not good" / "samajh nahi aata" are negative and removing "not"/"nahi" would flip the meaning.
No NLTK download needed - everything is self-contained so it runs offline.
"""
import re

import pandas as pd

from config import CLEAN_CSV, RAW_CSV

ENGLISH_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "am", "it", "its", "this", "that",
    "these", "those", "and", "or", "but", "of", "to", "in", "on", "at", "for", "with", "as", "by",
    "from", "we", "our", "us", "you", "your", "he", "she", "they", "them", "their", "i", "me", "my",
    "have", "has", "had", "do", "does", "did", "will", "would", "can", "could", "so", "than", "then",
    "there", "which", "who", "what", "when", "where", "all", "any", "some", "also", "just", "up",
}
HINGLISH_STOPWORDS = {
    "hai", "hain", "ho", "hota", "hoti", "hote", "tha", "thi", "the", "ka", "ki", "ke", "ko", "se",
    "mein", "me", "pe", "par", "aur", "ya", "to", "toh", "ye", "yeh", "wo", "woh", "ek", "bhi",
    "hi", "kuch", "sab", "kar", "karte", "karti", "karna", "dete", "deta", "dena", "jaate", "jata",
}
# Words that carry sentiment through negation - never remove
NEGATIONS = {"not", "no", "never", "nahi", "nhi", "na", "bilkul", "without", "nothing", "cant", "dont"}

STOPWORDS = (ENGLISH_STOPWORDS | HINGLISH_STOPWORDS) - NEGATIONS


def lemmatize(word: str) -> str:
    """Very light rule-based lemmatizer (plural / -ing / -ed endings)."""
    if len(word) <= 4 or word in {"nothing", "something", "anything", "everything", "during", "morning"}:
        return word
    for suffix, repl in (("ies", "y"), ("ing", ""), ("ed", ""), ("es", ""), ("s", "")):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            if suffix == "s" and word.endswith(("ss", "us", "is")):
                return word
            if suffix == "ed" and word.endswith("eed"):  # speed, need
                return word
            return word[: len(word) - len(suffix)] + repl
    return word


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-z\s]", " ", text)  # removes punctuation, digits, emojis
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS]
    tokens = [lemmatize(t) for t in tokens]
    return " ".join(tokens)


def rating_to_sentiment(rating: int) -> str:
    if rating >= 4:
        return "positive"
    if rating == 3:
        return "neutral"
    return "negative"


def run() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV)
    print("Shape:", df.shape)
    print("Missing values:\n", df.isna().sum())
    df = df.dropna(subset=["comment", "rating"]).drop_duplicates(subset=["student_id", "teacher", "comment"])
    df["clean_comment"] = df["comment"].apply(clean_text)
    df["sentiment"] = df["rating"].apply(rating_to_sentiment)
    df.to_csv(CLEAN_CSV, index=False)
    print(f"Saved cleaned data ({len(df)} rows) -> {CLEAN_CSV}")
    return df


if __name__ == "__main__":
    out = run()
    print(out[["comment", "clean_comment", "sentiment"]].head(5).to_string())
