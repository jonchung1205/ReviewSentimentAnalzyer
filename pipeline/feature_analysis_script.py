# ===============================================================
# Week 7 - Feature-Specific Sentiment Analysis
# ===============================================================

# --------------------------
# SETUP
# --------------------------
import pandas as pd
import numpy as np
import re
import nltk
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
from transformers import pipeline
import matplotlib.pyplot as plt

# Download required NLTK resources
nltk.download("punkt")
nltk.download("punkt_tab")

# ===============================================================
# STEP 1 — CLAUSE SPLITTING FUNCTION
# ===============================================================

def split_into_clauses(text):
    """
    Splits text into smaller clauses based on conjunctions like 'but', 'however', etc.
    This helps capture mixed sentiments within a single sentence.
    """
    parts = re.split(r'\b(?:but|however|although|though|while|and yet|whereas|nevertheless)\b', text, flags=re.IGNORECASE)
    clauses = [p.strip() for p in parts if len(p.strip()) > 3]
    return clauses


# ===============================================================
# STEP 2 — FEATURE BUCKET ASSIGNMENT
# ===============================================================

buckets = {
    "AI/Food Logging": [
        "log", "logging", "tracked", "scanner", "barcode", "photo", "recognition",
        "ai", "smart", "automatic", "food search", "nutrition", "macro", "meal",
        "recipe", "portion", "calorie", "database", "easy to log", "tedious"
    ],
    "Engagement/Coach Support": [
        "coach", "dietitian", "support", "help desk", "message", "chat", "motivation",
        "encouraging", "team", "accountability", "feedback", "responsive", "community"
    ],
    "Personalization": [
        "custom", "personalized", "tailored", "goal", "plan", "suggestions", "habits",
        "flexible", "fit my needs", "based on my", "recommend", "adaptive"
    ],
    "Cost/Value": [
        "price", "cost", "expensive", "cheap", "worth", "subscription", "pay",
        "money", "free", "trial", "refund", "cancel", "bargain", "hidden fee"
    ],
    "Usability/Technical": [
        "bug", "glitch", "error", "crash", "slow", "freeze", "interface", "design",
        "layout", "navigation", "user friendly", "hard to use", "update", "sync",
        "login", "account", "device", "frustrating"
    ]
}


def assign_bucket(sentence):
    """
    Assigns a feature bucket based on keyword matching.
    Returns the feature name if a keyword is found, else 'Other'.
    """
    for bucket, keywords in buckets.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", sentence, flags=re.IGNORECASE):
                return bucket
    return "Other"


# ===============================================================
# STEP 3 — SENTIMENT CLASSIFICATION (BERT)
# ===============================================================

# Load pretrained BERT sentiment pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Example input: a cleaned dataframe of reviews
# -------------------------------------------------------
#df = pd.read_csv("/Users/maliktraore/Omada_Health/SnapCal_GooglePlay_Cleaned.csv")  
#df['cleaned_content'] = df['cleaned_content'].astype(str)
# -------------------------------------------------------

def process_reviews(df):
    """
    Main function to process reviews at the sentence and clause level.
    Returns a DataFrame with sentiment results per feature bucket.
    """
    results = []

    for review in tqdm(df["content"], desc="Processing reviews"):
        sentences = sent_tokenize(review)
        for sent in sentences:
            clauses = split_into_clauses(sent)
            for clause in clauses:
                bucket = assign_bucket(clause)
                if bucket != "Other":
                    result = sentiment_analyzer(clause)[0]
                    results.append({
                        "clause": clause,
                        "bucket": bucket,
                        "label": result["label"],
                        "confidence": result["score"]
                    })
    sent_df = pd.DataFrame(results)
    return sent_df


# ===============================================================
# STEP 4 — AGGREGATION AND VISUALIZATION
# ===============================================================

def aggregate_sentiments(sent_df):
    """
    Aggregates sentiment counts by feature bucket and computes sentiment scores.
    """
    summary = (
        sent_df.groupby(["bucket", "label"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    summary["total"] = summary["POSITIVE"] + summary["NEGATIVE"]
    summary["positive_rate"] = summary["POSITIVE"] / summary["total"]
    summary["negative_rate"] = summary["NEGATIVE"] / summary["total"]
    summary["sentiment_score"] = summary["positive_rate"] - summary["negative_rate"]

    return summary


def plot_sentiment_summary(summary):
    """
    Visualizes sentiment scores by feature using horizontal bars.
    """
    plt.figure(figsize=(10, 6))
    colors = summary["sentiment_score"].apply(lambda x: "green" if x > 0 else "red")
    plt.barh(summary["bucket"], summary["sentiment_score"], color=colors)
    plt.xlabel("Sentiment Score (Positive - Negative)")
    plt.ylabel("Feature Category")
    plt.title("Feature-Specific Sentiment Analysis")
    plt.grid(axis="x", linestyle="--", alpha=0.6)
    plt.show()


# ===============================================================
# STEP 5 — EXAMPLE WORKFLOW
# ===============================================================

if __name__ == "__main__":
    # Example: load your preprocessed dataset
    df = pd.read_csv("C:/Users/togzh/omada-health/fooducate_google_play_raw.csv")
    df['content'] = df['content'].astype(str)

    # Process sentiment
    sent_df = process_reviews(df)

    # Show confidence histogram
    sent_df["confidence"].hist(bins=20, color="skyblue", edgecolor="black")
    plt.title("BERT Sentiment Confidence Distribution")
    plt.xlabel("Confidence Score")
    plt.ylabel("Frequency")
    plt.show()

    # Aggregate and plot results
    summary = aggregate_sentiments(sent_df)
    print(summary)

    plot_sentiment_summary(summary)

    # Export results for reporting
    sent_df.to_csv("Simple_APPSTORE_feature_sentiments_detailed.csv", index=False)
    summary.to_csv("Simple_APPSTORE_feature_sentiment_summary.csv", index=False)

    