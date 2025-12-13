import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from analysis_pipeline.cleaning_script import clean_text
from analysis_pipeline.sentiment_analysis import primitive_sentiment

st.title("Primitive Sentiment Analysis")
st.write("Upload raw reviews → clean text → run POSITIVE/NEGATIVE sentiment analysis.")

# -------------------------
# File Upload
# -------------------------
uploaded_file = st.file_uploader(
    "Upload raw scraped CSV file:",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Please upload a CSV file to begin.")
    st.stop()

# Validate extension
if not uploaded_file.name.endswith(".csv"):
    st.error("Please upload a valid CSV file ending in `.csv`.")
    st.stop()

# Load CSV
try:
    raw_df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Could not read CSV: {e}")
    st.stop()

# Check for required columns
REQUIRED_COLS = ["content"]
missing = [c for c in REQUIRED_COLS if c not in raw_df.columns]

if missing:
    st.error(
        f"Missing required column(s): {', '.join(missing)}.\n"
        "This file is NOT valid. Please upload output from the App Store or Google Play scraper."
    )
    st.stop()

st.success("CSV uploaded successfully!")

# -------------------------
# RAW DATA PREVIEW
# -------------------------
st.subheader("Raw Data Preview")
st.dataframe(raw_df.head())


# -------------------------
# CLEANING STEP
# -------------------------
st.subheader("Cleaning the Text")

with st.spinner("Cleaning review text..."):
    df = raw_df.copy()
    df["cleaned_content"] = df["content"].fillna("").apply(clean_text)

# Show before/after comparison
st.write("### Before and After Cleaning")
st.dataframe(df[["content", "cleaned_content"]].head())
st.success("Cleaning complete!")


# -------------------------
# SENTIMENT ANALYSIS
# -------------------------
st.subheader("Running Primitive Sentiment Analysis")

with st.spinner("Analyzing sentiment..."):
    sentiment_df = primitive_sentiment(df)

st.success("Sentiment analysis complete!")

# -------------------------
# VISUALIZATIONS
# -------------------------
st.subheader("Sentiment Overview")

# Pie chart
good_count = (sentiment_df["sentiment"] == "POSITIVE").sum()
bad_count  = (sentiment_df["sentiment"] == "NEGATIVE").sum()

fig, ax = plt.subplots(figsize=(4, 4)) 
ax.pie(
    [good_count, bad_count],
    labels=["Positive", "Negative"],
    autopct="%1.1f%%",
    startangle=90
)
ax.axis("equal")
st.pyplot(fig)


# -------------------------
# CONFIDENCE SCORE HISTOGRAM
# -------------------------
st.subheader("Confidence Score Distribution")

fig2, ax2 = plt.subplots()
ax2.hist(sentiment_df["confidence"], bins=20, color="skyblue", edgecolor="black")
ax2.set_xlabel("Confidence Score")
ax2.set_ylabel("Number of Reviews")
ax2.set_title("Distribution of Sentiment Confidence Scores")
st.pyplot(fig2)


# -------------------------
# DOWNLOAD RESULTS
# -------------------------
st.subheader("⬇ Download Results")

final_output = df.join(sentiment_df.drop(columns=["review"]))
csv_download = final_output.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Processed Sentiment CSV",
    data=csv_download,
    file_name="processed_sentiment_results.csv",
    mime="text/csv"
)
