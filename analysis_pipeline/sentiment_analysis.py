import pandas as pd
from transformers import pipeline as hf_pipeline

def primitive_sentiment(df: pd.DataFrame, text_column: str = "cleaned_content"):
    """
    Runs simple POSITIVE/NEGATIVE sentiment analysis on entire reviews.
    Matches the Colab script behavior exactly.
    """

    model = hf_pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    results = []

    # Batch processing for speed
    texts = df[text_column].fillna("").tolist()
    outputs = model(texts, truncation=True)

    for review, output in zip(texts, outputs):
        label = output["label"]
        score = float(output["score"])

        results.append({
            "review": review,
            "sentiment": label,
            "confidence": score
        })

    return pd.DataFrame(results)
