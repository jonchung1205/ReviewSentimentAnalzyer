import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from analysis_pipeline.cleaning_script import clean_text
from analysis_pipeline.feature_sentiment import analyze_sentiment


# -----------------------------------------
# PAGE HEADER
# -----------------------------------------
st.title("Feature-Specific Sentiment Analysis")
st.write("Upload raw scraped reviews → clean them → run feature-level sentiment analysis.")


# -----------------------------------------
# FILE UPLOAD
# -----------------------------------------
uploaded_file = st.file_uploader("Upload RAW scraped CSV", type=["csv"])

if uploaded_file is None:
    st.info("Please upload a RAW CSV file from the App Store or Google Play scraper.")
    st.stop()


# -----------------------------------------
# LOAD RAW DATA
# -----------------------------------------
try:
    raw_df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Could not read CSV: {e}")
    st.stop()


# Ensure required column exists
if "content" not in raw_df.columns:
    st.error(
        "The file you uploaded does not contain the required column: **content**.\n"
        "This means it is not raw scraped data.\n\n"
        "**Please upload the output from the App Store or Google Play scraper.**"
    )
    st.stop()


st.success("Raw CSV loaded successfully.")
st.subheader("Raw Data Preview")
st.dataframe(raw_df.head())


# -----------------------------------------
# CLEANING STEP
# -----------------------------------------
st.subheader("Cleaning Text")

with st.spinner("Cleaning review text..."):
    df = raw_df.copy()
    df["cleaned_content"] = df["content"].fillna("").apply(clean_text)

st.write("### Before → After Cleaning")
st.dataframe(df[["content", "cleaned_content"]].head())

st.success("Cleaning complete!")


# -----------------------------------------
# FEATURE-SPECIFIC SENTIMENT ANALYSIS
# -----------------------------------------
st.subheader("Running Feature-Specific Sentiment Analysis")

with st.spinner("Analyzing sentiment across features..."):
    result_df, summary_df = analyze_sentiment(df, text_column="cleaned_content")

st.success("Feature-level sentiment analysis complete!")


# -----------------------------------------
# CONFIDENCE HISTOGRAM
# -----------------------------------------
st.subheader("Model Confidence Distribution")

fig, ax = plt.subplots(figsize=(6, 4))  # Smaller figure
result_df["confidence"].hist(bins=25, edgecolor="black", ax=ax)
ax.set_xlabel("Confidence Score")
ax.set_ylabel("Frequency")
ax.set_title("Confidence Distribution")

st.pyplot(fig)


# -----------------------------------------
# FEATURE SUMMARY TABLE
# -----------------------------------------
st.subheader("Feature-Level Sentiment Summary")
st.dataframe(summary_df)


# -----------------------------------------
# BAR CHART: SENTIMENT SCORE BY FEATURE
# -----------------------------------------
st.subheader("Sentiment Score by Feature")

fig2, ax2 = plt.subplots(figsize=(8, 5))

colors = ["#4CAF50" if x >= 0 else "#F44336" for x in summary_df["sentiment_score"]]
summary_df["sentiment_score"].plot(kind="barh", ax=ax2, color=colors)

ax2.set_xlabel("Sentiment Score")
ax2.set_ylabel("Feature")
ax2.set_title("Feature Sentiment Ranking")

st.pyplot(fig2)


# -----------------------------------------
# DOWNLOAD RESULTS
# -----------------------------------------
st.subheader("⬇ Download Results")

final = df.join(result_df)

st.download_button(
    label="Download Full Feature-Specific Sentiment CSV",
    data=final.to_csv(index=False).encode("utf-8"),
    file_name="feature_sentiment_results.csv",
    mime="text/csv"
)
