import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# ---- PATH SETUP ----
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# ---- IMPORT BACKEND PIPELINE ----
from sentiment_analysis import run_sentiment_analysis
from text_cleaning import clean_text


# ------------------------- STREAMLIT UI -------------------------

st.title("Primitive Sentiment Analysis Tool")

uploaded_file = st.file_uploader("Upload CSV of scraped reviews", type=["csv"])

run_button = st.button("Run Sentiment Analysis")

df = None

# ---- LOAD CSV ----
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write(f"Loaded **{len(df)}** reviews.")
    st.dataframe(df.head())


# ---------------------- RUN ANALYSIS ----------------------------
if run_button:

    if df is None:
        st.error("Please upload a CSV file first.")
        st.stop()

    with st.spinner("Cleaning text and running sentiment analysis..."):
        
        # Clean column names & process text
        df["cleaned_text"] = df["review"].astype(str).apply(clean_text)
        
        # Run primitive sentiment analysis script
        results = run_sentiment_analysis(df["cleaned_text"].tolist())

        # Expecting results like: [{"sentiment": ..., "confidence": ...}, ...]
        df["sentiment"] = [r["sentiment"] for r in results]
        df["confidence"] = [r["confidence"] for r in results]

    st.success("Analysis complete!")

    # ------------------------- SHOW RESULTS -------------------------

    st.subheader("Processed Data Preview")
    st.dataframe(df.head(20))

    # ---------------------- BAR CHART SUMMARY ----------------------

    st.subheader("Overall Sentiment Distribution")

    sentiment_counts = df["sentiment"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 5))
    sentiment_counts.plot(kind="bar", color=["#4CAF50", "#F44336", "#FFC107"], ax=ax)
    ax.set_title("General Sentiment Summary")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    # --------------------- OPTIONAL CONFIDENCE HISTOGRAM ---------------------

    st.subheader("Model Confidence Distribution")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    df["confidence"].hist(bins=20, edgecolor="black", ax=ax2)
    ax2.set_xlabel("Confidence")
    ax2.set_ylabel("Frequency")
    st.pyplot(fig2)

