"""
T2: Synthetic dataset generator.
Creates data/feedback.csv with 450 student comments (English + Hinglish mix).

Columns: student_id, teacher, subject, rating, comment, date
Each teacher has a "quality profile" so the final analysis shows real differences.
"""
import random
from datetime import date, timedelta

import pandas as pd

from config import RAW_CSV, RANDOM_STATE

random.seed(RANDOM_STATE)

# teacher -> (subject, probability weights for [positive, neutral, negative])
TEACHERS = {
    "Prof. Sharma": ("Artificial Intelligence", (0.75, 0.15, 0.10)),
    "Dr. Verma": ("Data Structures", (0.55, 0.25, 0.20)),
    "Prof. Gupta": ("Database Systems", (0.30, 0.30, 0.40)),
    "Dr. Singh": ("Operating Systems", (0.45, 0.25, 0.30)),
    "Prof. Mishra": ("Artificial Intelligence", (0.20, 0.25, 0.55)),
}

# Phrase pools: topic -> sentiment -> list of comments
POOL = {
    "Teaching": {
        "positive": [
            "Sir ka padhane ka tarika bahut accha hai, sab kuch easily samajh aata hai",
            "Excellent teaching, concepts are explained very clearly with examples",
            "Mam bahut acche se explain karti hain, doubts clear ho jaate hain",
            "Great teacher, always patient and the lectures are engaging",
            "Samjhane ka style kamaal ka hai, real life examples dete hain",
            "Very helpful faculty, explains difficult topics in a simple way",
            "Lecture ekdum mast hota hai, class mein maza aata hai",
            "Best teacher, makes the subject interesting and easy to follow",
        ],
        "neutral": [
            "Teaching is okay, kuch topics samajh aate hain kuch nahi",
            "Lectures are average, nothing special but not bad either",
            "Padhai theek thaak hai, kabhi accha kabhi average",
            "The teaching style is fine, can be improved a little",
        ],
        "negative": [
            "Bahut tez padhate hain, kuch samajh nahi aata",
            "Teaching is boring and the lectures are confusing",
            "Concepts clear nahi hote, sirf slides padh ke chale jaate hain",
            "Very poor explanation, students are not able to understand anything",
            "Class mein bilkul maza nahi aata, lecture bahut boring hai",
            "Teacher does not clear doubts and ignores our questions",
            "Padhane ka tarika bekaar hai, speed bahut fast hai",
            "Terrible teaching, we have to study everything on our own",
        ],
    },
    "Labs/Practicals": {
        "positive": [
            "Lab sessions are very useful, practical knowledge mila",
            "Practical classes bahut helpful hain, hands-on experience accha hai",
            "Lab mein sab kuch implement karna sikhaya, really good",
            "Good lab guidance and the experiments are well planned",
        ],
        "neutral": [
            "Lab is fine but sometimes the systems are slow",
            "Practicals theek hain, thoda aur time milna chahiye",
            "Lab work is okay, nothing great",
        ],
        "negative": [
            "Lab mein computers kaam nahi karte, practical ho hi nahi paata",
            "Practical sessions are a waste of time, no proper guidance",
            "Lab sessions bahut kam hote hain aur experiments samajh nahi aate",
            "Poor lab facilities and the instructor never helps in practicals",
        ],
    },
    "Exams/Evaluation": {
        "positive": [
            "Exams are fair and the paper was based on what was taught",
            "Evaluation bahut fair hai, marks sahi milte hain",
            "Assignments are useful and feedback on them is quick",
            "Paper pattern clear tha aur syllabus ke andar tha",
        ],
        "neutral": [
            "Exam was moderate, some questions were tricky",
            "Assignments theek the, thoda zyada the but manageable",
            "Paper average tha, na bahut easy na bahut hard",
        ],
        "negative": [
            "Paper bahut tough tha aur syllabus se bahar ke questions aaye",
            "Marking is unfair and we never get proper feedback on exams",
            "Too many assignments and the deadlines are unreasonable",
            "Exam pattern kabhi clear nahi hota, bahut confusion rehta hai",
        ],
    },
    "Course Content": {
        "positive": [
            "Syllabus is up to date and very relevant for placements",
            "Course content bahut useful hai, industry ke kaam aayega",
            "Study material is well organised and easy to follow",
            "Good coverage of topics, notes bhi bahut helpful hain",
        ],
        "neutral": [
            "Syllabus is okay, some topics feel outdated",
            "Content theek hai, par examples aur hone chahiye",
            "Course is average, covers basics only",
        ],
        "negative": [
            "Syllabus is outdated and not useful for jobs",
            "Notes aur study material bilkul nahi diye jaate",
            "Course content is too heavy and badly organised",
            "Syllabus bahut zyada hai aur time kam, complete nahi hota",
        ],
    },
    "Behaviour/Support": {
        "positive": [
            "Very friendly and approachable, always ready to help students",
            "Sir bahut supportive hain, kabhi bhi doubt puch sakte hain",
            "Respectful teacher who motivates the whole class",
            "Mam hamesha time pe aati hain aur students ki help karti hain",
        ],
        "neutral": [
            "Behaviour is okay, not very friendly but not rude",
            "Teacher theek hain, kabhi kabhi class late start hoti hai",
        ],
        "negative": [
            "Teacher is rude and does not respect students",
            "Sir hamesha late aate hain aur class jaldi khatam kar dete hain",
            "Not approachable at all, students are scared to ask questions",
            "Bahut strict aur rude behaviour hai, koi support nahi milta",
        ],
    },
}

EXTRA = {
    "positive": ["Overall great experience.", "Highly recommended!", "Mazaa aa gaya.", "Keep it up sir.", ""],
    "negative": ["Needs improvement.", "Please fix this.", "Bahut disappointing hai.", "Hope things change.", ""],
    "neutral": ["Overall okay.", "Chal jata hai.", "Could be better.", ""],
}

RATING_BY_SENT = {
    "positive": [5, 5, 4, 4, 4],
    "neutral": [3, 3, 3, 2, 4],
    "negative": [1, 1, 2, 2, 1],
}


def make_comment(sentiment: str, topic: str) -> str:
    base = random.choice(POOL[topic][sentiment])
    extra = random.choice(EXTRA[sentiment])
    return f"{base}. {extra}" if extra else f"{base}."


def generate(n: int = 450) -> pd.DataFrame:
    rows = []
    start = date(2026, 1, 5)
    for _ in range(n):
        teacher = random.choice(list(TEACHERS))
        subject, weights = TEACHERS[teacher]
        sentiment = random.choices(["positive", "neutral", "negative"], weights=weights)[0]
        topic = random.choice(list(POOL))
        comment = make_comment(sentiment, topic)
        rating = random.choice(RATING_BY_SENT[sentiment])

        # ~6% noisy rows: rating does not match comment (used in mismatch analysis)
        if random.random() < 0.06:
            rating = random.choice([1, 2, 3, 4, 5])

        rows.append(
            {
                "student_id": f"S{1000 + random.randint(0, 299)}",
                "teacher": teacher,
                "subject": subject,
                "rating": rating,
                "comment": comment,
                "date": (start + timedelta(days=random.randint(0, 180))).isoformat(),
            }
        )
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


if __name__ == "__main__":
    df = generate()
    df.to_csv(RAW_CSV, index=False)
    print(f"Saved {len(df)} rows -> {RAW_CSV}")
    print(df.head())
