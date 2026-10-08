"""T8.2: Predict sentiment + topic for a single new comment."""
import joblib

from config import MODEL_PATH
from preprocess import clean_text
from topics import get_topic

_model = None


def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_comment(comment: str) -> dict:
    model = load_model()
    cleaned = clean_text(comment)
    label = model.predict([cleaned])[0]
    proba = {c: float(round(p, 3)) for c, p in zip(model.classes_, model.predict_proba([cleaned])[0])}
    return {"sentiment": label, "confidence": float(max(proba.values())), "probabilities": proba,
            "topic": get_topic(comment), "cleaned": cleaned}


if __name__ == "__main__":
    for c in ["Sir bahut accha padhate hain, samajh aa jata hai", "Lab mein computers kaam nahi karte",
              "Paper was okay, nothing special"]:
        print(c, "->", predict_comment(c))
