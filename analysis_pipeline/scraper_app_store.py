from app_store_web_scraper import AppStoreEntry, AppStoreSearch
import pandas as pd
import time


def lookup_app_id(app_name, country="us"):
    """
    Look up the App Store ID for a given app name.
    Returns: app_id (int) or None.
    """
    try:
        results = AppStoreSearch(term=app_name, country=country).fetch()

        if not results or "results" not in results or len(results["results"]) == 0:
            print(f" No app found for '{app_name}'.")
            return None

        first = results["results"][0]
        app_id = first.get("trackId")

        if not app_id:
            print(f" Failed to extract App ID for '{app_name}'.")
            return None

        print(f" Found App ID for '{app_name}': {app_id}")
        return app_id

    except Exception as e:
        print(f"Error during lookup: {e}")
        return None



def scrape_app_reviews(app_id, app_name=None, country="us", output_filename=None):
    """
    Scrape all App Store reviews given an app_id.
    """
    print(f"\n Scraping reviews for App ID {app_id} ({app_name})")

    try:
        app = AppStoreEntry(app_id=app_id, country=country)
        reviews_gen = app.reviews()
    except Exception as e:
        print(f" Could not initialize scraper: {e}")
        return None

    all_reviews = []

    try:
        for review in reviews_gen:
            all_reviews.append({
                'id': review.id,
                'date': review.date,
                'user_name': review.user_name,
                'rating': review.rating,
                'title': review.title,
                'content': review.content,
            })

            if len(all_reviews) % 50 == 0:
                print(f"… {len(all_reviews)} reviews scraped")
    except Exception as e:
        print(f" Error during scraping: {e}")
        time.sleep(5)

    print(f" Total reviews scraped: {len(all_reviews)}")

    df = pd.DataFrame(all_reviews)

    if output_filename is None:
        safe = app_name.replace(" ", "_") if app_name else f"app_{app_id}"
        output_filename = f"{safe}_{country}_reviews.csv"

    df.to_csv(output_filename, index=False)
    print(f"💾 Saved to {output_filename}")

    return df



def scrape_by_app_names(app_names, country="us"):
    """
    Accepts a list or single app name.
    Returns dict: {app_name: DataFrame}
    """
    if isinstance(app_names, str):
        app_names = [app_names]

    results = {}

    for name in app_names:
        app_id = lookup_app_id(name, country)

        if app_id is None:
            print(f"Skipping '{name}' — no valid App ID.\n")
            results[name] = None
            continue

        df = scrape_app_reviews(app_id, app_name=name, country=country)
        results[name] = df

    return results
