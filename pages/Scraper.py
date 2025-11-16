import streamlit as st
import pandas as pd
import sys
import os

# -----------------------------------------------------------
# FIX IMPORT PATHS (same as your other working Streamlit page)
# -----------------------------------------------------------

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

DATA_RAW = os.path.join(project_root, "data", "raw")
os.makedirs(DATA_RAW, exist_ok=True)

# -----------------------------------------------------------
# IMPORT YOUR APP STORE SCRAPER
# -----------------------------------------------------------
from app_store_web_scraper import AppStoreEntry


def scrape_appstore(app_id, country="us"):
    """
    Scrapes App Store reviews using AppStoreEntry.
    Returns a DataFrame.
    """
    app = AppStoreEntry(app_id=app_id, country=country)

    records = []
    for r in app.reviews():
        records.append({
            "app_id": app_id,
            "date": r.date,
            "rating": r.rating,
            "title": r.title,
            "content": r.content,
            "user_name": r.user_name
        })

    return pd.DataFrame(records)


# -----------------------------------------------------------
# STREAMLIT UI
# -----------------------------------------------------------

st.title("📱 App Store Scraper")

st.write("Enter App Store IDs and scrape reviews directly into the app.")

# Inputs
app_ids_raw = st.text_input(
    "App Store App IDs (comma-separated)",
    placeholder="Example: 398436747, 333903271"
)

country = st.text_input("Country Code", value="us")

run_button = st.button("Run Scraper", type="primary")

# Output containers
status_area = st.empty()
preview_area = st.empty()
download_area = st.empty()

# -----------------------------------------------------------
# SCRAPING HANDLER
# -----------------------------------------------------------

if run_button:
    if not app_ids_raw.strip():
        st.error("Please enter at least one app ID.")
        st.stop()

    app_ids = [x.strip() for x in app_ids_raw.split(",") if x.strip()]
    all_frames = []

    with st.spinner("Scraping App Store reviews..."):
        for app_id in app_ids:
            try:
                status_area.write(f"🔍 Scraping app ID: **{app_id}**")
                df = scrape_appstore(app_id, country)
                df["platform"] = "App Store"
                all_frames.append(df)
            except Exception as e:
                status_area.error(f"Error scraping {app_id}: {e}")

    if not all_frames:
        status_area.error("No data was scraped.")
        st.stop()

    final_df = pd.concat(all_frames).reset_index(drop=True)

    status_area.success(
        f"Scraped **{len(final_df)} reviews** from **{len(app_ids)} app(s)**."
    )

    preview_area.subheader("Preview of Scraped Reviews")
    preview_area.dataframe(final_df.head(), use_container_width=True)

    # Save raw file
    output_path = os.path.join(DATA_RAW, "appstore_scraped_raw.csv")
    final_df.to_csv(output_path, index=False)

    # CSV Download Button
    download_area.download_button(
        label="Download Full CSV",
        data=final_df.to_csv(index=False),
        file_name="appstore_scraped_reviews.csv",
        mime="text/csv"
    )
