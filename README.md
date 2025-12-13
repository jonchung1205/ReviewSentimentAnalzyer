# Review Sentiment Analyzer
## Intended Use Case

This app is **best suited for sentiment analysis of nutrition, wellness, and food-tracking applications**, where user feedback is often **feature-specific** rather than purely overall sentiment.

Examples of common product questions this tool helps answer:
- How do users feel about **AI-powered food logging**?
- Are users satisfied with **personalized recommendations**?
- Is **human coaching or engagement** perceived as valuable?
- Are pricing and subscription models a source of negative sentiment?
- Are technical issues impacting retention?

The feature-level sentiment breakdown is especially useful for **product teams, growth teams, and consulting analyses** focused on understanding *why* users feel a certain way — not just *how* they feel.

---

## Tech Stack

### Frontend
- **Streamlit** — interactive web UI for searching apps, scraping reviews, and downloading datasets

### Data Handling
- **Pandas** — tabular data processing and CSV export
- **NumPy** — numerical operations

### Scraping
- **google-play-scraper** — Google Play Store reviews
- **app-store-web-scraper** — Apple App Store reviews
- **Requests / urllib3** — networking utilities

### NLP & Machine Learning
- **NLTK** — tokenization, stopword removal, lemmatization
- **Hugging Face Transformers** — pretrained transformer models for sentiment analysis
- **SentencePiece** — tokenizer support
- **Matplotlib** — exploratory visualizations

---

## NLP Pipeline Overview

The app uses a **three-stage NLP pipeline** designed to support both high-level and feature-specific sentiment insights.

---

### 1. Text Cleaning & Normalization

Raw app store reviews are cleaned using a robust preprocessing pipeline that includes:

- Lowercasing
- Emoji removal
- Unicode-safe punctuation & symbol filtering
- Whitespace normalization
- Stopword removal
- Lemmatization

Cleaned text is stored in new columns (e.g. `cleaned_content`) to preserve original metadata.

This step ensures consistent, high-quality input for downstream transformer models.

---

### 2. Primitive (Overall) Sentiment Analysis

A **baseline sentiment analyzer** is applied to full review text using:

- **Model:** `distilbert-base-uncased-finetuned-sst-2-english`
- **Output:** POSITIVE / NEGATIVE sentiment + confidence score

This provides a fast, coarse-grained view of overall user sentiment across reviews.

Use cases:
- Tracking general sentiment trends
- Comparing sentiment across apps or versions
- Sanity-checking feature-level results

---

### 3. Feature-Specific Sentiment Analysis (Core Insight Engine)

To capture *why* users feel a certain way, the app performs **feature-level sentiment analysis** using a hybrid approach:

#### Clause-Level Parsing
- Reviews are split into sentences
- Sentences are further split into clauses (e.g. handling “but”, “however”, etc.)
- This allows mixed-sentiment reviews to be analyzed accurately

#### Feature Bucketing
Each clause is matched against curated keyword dictionaries for key product dimensions:

- **AI / Food Logging**
- **Engagement & Coaching Support**
- **Personalization**
- **Cost & Value**
- **Usability & Technical Performance**

#### Sentiment Modeling
- **Model:** `cardiffnlp/twitter-roberta-base-sentiment-latest`
- Outputs: POSITIVE / NEGATIVE / NEUTRAL + confidence

#### Aggregated Outputs
- Clause-level sentiment table
- Feature-level sentiment summary:
  - Positive rate
  - Negative rate
  - Net sentiment score

This enables direct comparisons such as:
> “Users love personalization but are frustrated by usability issues.”

---

## Example Outputs

- Cleaned review dataset (CSV)
- Overall sentiment classification per review
- Clause-level feature sentiment table
- Feature-level sentiment summary with ranking

---

## Deployment

This app is deployed using **Streamlit Cloud** and can be accessed via a public URL.

### How to Use the Deployed App
1. Select **Apple App Store** or **Google Play**
2. Search for an app by name  
3. (Optional) Paste a Google Play app URL if search results are limited
4. Scrape reviews (up to 500 per app)
5. Download results as a CSV for offline analysis or modeling

---

## Notes & Limitations

- Feature classification relies on **keyword-based matching** (interpretable but not exhaustive)
- Sentiment models are pretrained and not domain-fine-tuned
- Results should be interpreted as **directional insights**, not absolute truth

---

## Future Improvements

- Fine-tuning sentiment models on nutrition-specific review data
- Multi-label feature assignment per clause
- Time-series sentiment tracking
- Interactive feature-level dashboards
- Support for additional app categories

---

## License

This project is intended for **educational, analytical, and consulting use**.

