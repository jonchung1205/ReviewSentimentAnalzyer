import streamlit as st
import pandas as pd
import requests
from app_store_web_scraper import AppStoreEntry
from google_play_scraper import Sort, reviews, search, app as gplay_app
import re

MAX_REVIEWS = 500

# ==================== INITIALIZATION ====================

if 'selected_app_id' not in st.session_state:
    st.session_state.selected_app_id = None
if 'selected_app_name' not in st.session_state:
    st.session_state.selected_app_name = None
if 'scraped_df' not in st.session_state:
    st.session_state.scraped_df = None
if 'platform' not in st.session_state:
    st.session_state.platform = "App Store"

# ==================== SEARCH FUNCTIONS ====================
def search_appstore(app_name):
    url = "https://itunes.apple.com/search"
    params = {"term": app_name, "entity": "software", "limit": 10}
    try:
        resp = requests.get(url, params=params).json()
    except Exception as e:
        return {"error": str(e)}, []

    results = []
    for item in resp.get("results", []):
        results.append({
            "app_id": item.get("trackId"),
            "name": item.get("trackName"),
            "developer": item.get("sellerName"),
            "url": item.get("trackViewUrl")
        })
    return None, results

def search_gplay(app_name):
    try:
        results = search(app_name, lang="en", country="us")
    except Exception as e:
        return {"error": str(e)}, []

    parsed = []
    for r in results[:10]:
        if r.get("appId"):
            parsed.append({
                "app_id": r.get("appId"),
                "name": r.get("title"),
                "developer": r.get("developer"),
                "url": r.get("url")
            })
    return None, parsed

def get_package_from_url(url: str):
    match = re.search(r'id=([a-zA-Z0-9._]+)', url)
    if not match:
        return None
    package_name = match.group(1)
    try:
        info = gplay_app(package_name, lang="en", country="us")
        return {"app_id": package_name, "name": info.get("title"), "developer": info.get("developer")}
    except:
        return {"app_id": package_name, "name": "(From URL)", "developer": ""}

# ==================== SCRAPING FUNCTIONS ====================
def scrape_appstore_reviews(app_id, country="us", max_reviews=MAX_REVIEWS):
    app = AppStoreEntry(app_id=app_id, country=country)
    try:
        reviews_gen = app.reviews()
    except Exception as e:
        st.warning(f"Error fetching App Store reviews: {e}")
        return pd.DataFrame()

    parsed_reviews = []
    for i, r in enumerate(reviews_gen):
        if i >= max_reviews:
            break
        parsed_reviews.append({
            "platform": "app_store",
            "app_id": app_id,
            "date": getattr(r, "date", None),
            "rating": getattr(r, "rating", None),
            "title": getattr(r, "title", None),
            "content": getattr(r, "content", None),
            "user_name": getattr(r, "user_name", None),
        })
    return pd.DataFrame(parsed_reviews)

def scrape_gplay_reviews(app_id, max_reviews=MAX_REVIEWS):
    all_reviews = []
    next_token = None
    while len(all_reviews) < max_reviews:
        try:
            batch, next_token = reviews(
                app_id,
                lang="en",
                sort=Sort.NEWEST,
                count=100,
                continuation_token=next_token
            )
        except Exception as e:
            st.warning(f"Error fetching Google Play reviews: {e}")
            break
        if not batch:
            break
        for r in batch:
            all_reviews.append({
                "platform": "google_play",
                "app_id": app_id,
                "date": r.get("at"),
                "rating": r.get("score"),
                "title": r.get("reviewId"),
                "content": r.get("content"),
                "user_name": r.get("userName"),
            })
            if len(all_reviews) >= max_reviews:
                break
        if next_token is None:
            break
    return pd.DataFrame(all_reviews[:max_reviews])

# ==================== STREAMLIT INTERFACE ====================
st.title("📱 App Review Scraper & Downloader")
st.write("Search any mobile app and scrape up to 500 reviews from either store.")
st.write("Note: If you want to scrape from Google Play and the App Name does not show up in the results, you will need to paste the URL and hit Scrape and Download (ex. https://play.google.com/store/apps/details?id=com.wsl.noom&hl=en_US)")

app_name_input = st.text_input("Enter App Name")

st.session_state.platform = st.radio(
    "Choose Platform",
    ["App Store", "Google Play"],
    horizontal=True
)

# --- SEARCH BUTTON ---
def handle_search():
    if not app_name_input.strip():
        st.error("Please enter an app name.")
        return

    st.session_state.search_results = []
    st.session_state.selected_app_id = None
    st.session_state.selected_app_name = None
    st.session_state.scraped_df = None

    if st.session_state.platform == "App Store":
        error, results = search_appstore(app_name_input)
    else:
        error, results = search_gplay(app_name_input)

    if error:
        st.error(f"Error: {error}")
    elif not results:
        st.error("No apps found.")
    else:
        st.session_state.search_results = results
        st.success(f"Found {len(results)} results in {st.session_state.platform}.")

st.button("Search App", on_click=handle_search)

# --- SELECT APP & SCRAPE ---
if st.session_state.search_results:
    st.subheader(f"Select App from {st.session_state.platform} Results")
    app_options = {f"{r['name']} — {r['developer']}": r["app_id"] for r in st.session_state.search_results if r.get("app_id")}

    if not app_options:
        st.warning("No valid apps with IDs found.")
    else:
        labels = list(app_options.keys())
        default_index = 0
        if st.session_state.selected_app_name in labels:
            default_index = labels.index(st.session_state.selected_app_name)

        selected_label = st.selectbox("Results", options=labels, index=default_index, key="selected_label_box")
        st.session_state.selected_app_id = app_options[selected_label]
        st.session_state.selected_app_name = selected_label
        st.info(f"App to scrape: **{selected_label}** | ID: `{st.session_state.selected_app_id}`")

        # --- URL fallback ---
        st.markdown(
            "If the app is not listed above or the ID is missing, you can paste the Google Play URL below:"
        )
        gplay_url_input = st.text_input("Google Play URL (optional)")
        if gplay_url_input.strip():
            info = get_package_from_url(gplay_url_input.strip())
            if info:
                st.session_state.selected_app_id = info["app_id"]
                st.session_state.selected_app_name = f"{info['name']} — {info['developer']}"
                st.info(f"Using App from URL: {info['name']} | ID: {info['app_id']}")

        def handle_scrape():
            if not st.session_state.selected_app_id:
                st.warning("Please select an app first.")
                return
            st.session_state.scraped_df = None
            with st.spinner(f"Scraping up to {MAX_REVIEWS} reviews…"):
                if st.session_state.platform == "App Store":
                    df = scrape_appstore_reviews(st.session_state.selected_app_id, max_reviews=MAX_REVIEWS)
                else:
                    df = scrape_gplay_reviews(st.session_state.selected_app_id, max_reviews=MAX_REVIEWS)
            if not df.empty:
                st.session_state.scraped_df = df
                st.success(f"Successfully scraped {len(df)} reviews! You can download the CSV below.")
            else:
                st.warning("No reviews found.")

        st.button("Scrape Reviews", on_click=handle_scrape)

# --- DOWNLOAD CSV ---
if st.session_state.scraped_df is not None:
    df = st.session_state.scraped_df
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Reviews as CSV",
        data=csv_data,
        file_name=f"{st.session_state.platform.lower().replace(' ', '_')}_{st.session_state.selected_app_id}_reviews.csv",
        mime="text/csv"
    )
