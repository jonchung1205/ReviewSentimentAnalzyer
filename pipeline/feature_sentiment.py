# -------------------------
# Environment setup
# -------------------------
import pandas as pd
import numpy as np
import re
import nltk
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
from transformers import pipeline
import matplotlib.pyplot as plt
import time

# --- Configuration ---
# This is the output file from your clean_fast_v2.py script
CLEANED_INPUT_FILE = 'fooducate_us_clean.csv' 
# This is the main column we will analyze
TEXT_COLUMN = 'cleaned_content' 

print("Downloading NLTK models (if not already present)...")
nltk.download("punkt", quiet=True)
nltk.download('punkt_tab', quiet=True)


# -----------------------------------------------
# STEP 1 & 2: BUCKET & CLAUSE FUNCTIONS
# -----------------------------------------------

BUCKET_KEYWORDS = {
    "AI/Food Logging": [
        # Core logging actions
        "log", "logging", "logged", "track", "tracking", "tracked", "record", "recording",
        "enter", "entering", "input", "add food", "adding food",
        
        # Scanning & recognition
        "scan", "scanner", "scanning", "barcode", "bar code",
        "photo", "picture", "image", "camera", "snap", "take a picture",
        "recognize", "recognition", "detect", "detects", "identifying",
        
        # AI/Tech terms
        "ai", "artificial intelligence", "machine learning", "smart",
        "automatic", "automatically", "suggests food", "food suggestion",
        
        # Food database
        "database", "food search", "search for food", "find food",
        "food library", "food list", "can't find", "missing food",
        "limited options", "extensive database",
        
        # Nutrition tracking
        "calorie", "calories", "cal", "nutrition", "nutritional", "nutrient", "nutrients",
        "macro", "macros", "protein", "carb", "carbs", "fat", "fiber",
        "portion", "serving", "serving size",
        
        # Meals & recipes
        "recipe", "recipes", "meal", "meals", "breakfast", "lunch", "dinner", "snack",
        "meal prep", "what i ate", "food diary", "food journal",
        
        # Common phrases
        "easy to log", "hard to log", "tedious", "time consuming to log",
        "quick entry", "convenient logging"
    ],

    "Engagement/Coach Support": [
        # Coach/Expert titles
        "coach", "coaches", "dietitian", "nutritionist", "trainer",
        "mentor", "advisor", "counselor", "specialist",
        
        # Human connection
        "support", "support team", "customer service", "help desk",
        "human", "real person", "actual person", "live person",
        "expert", "professional", "staff", "team",
        
        # Interaction types
        "check in", "check-in", "checking in", "follow up", "following up",
        "message", "messaging", "messages", "text", "texting", "texts",
        "chat", "chatting", "conversation", "talk", "talking",
        "respond", "response", "replies", "reply", "answered",
        
        # Support quality
        "accountability", "accountable", "keep me on track",
        "motivation", "motivate", "motivating", "motivational", "motivated",
        "encouragement", "encouraging", "supportive", "caring",
        "advice", "guidance", "tips", "suggestions", "recommended",
        "feedback", "helpful", "knowledgeable",
        
        # Frequency & availability
        "reminder", "reminders", "daily message", "weekly check",
        "available", "accessible", "responsive", "quick to respond",
        "slow to respond", "never responded", "didn't hear back",
        
        # Community
        "community", "forum", "group", "groups", "discussion",
        "other users", "members", "connect with others",
        
        # Common phrases
        "someone to talk to", "1-on-1", "one on one", "one-on-one",
        "assigned coach", "my coach", "the coach", "my dietitian"
    ],

    "Personalization": [
        # Customization
        "custom", "customized", "customize", "customizable",
        "personal", "personalized", "personalize",
        "tailored", "tailor", "adapted", "adaptive", "adjust", "adjusted",
        
        # User-specific
        "specific to me", "for me", "fit my needs", "fits my lifestyle",
        "my situation", "individual", "individualized", "unique",
        
        # Goals & targets
        "goal", "goals", "objective", "objectives", "target", "targets",
        "weight goal", "fitness goal", "health goal", "lose weight",
        "gain weight", "maintain weight", "tone", "build muscle",
        
        # Plans & programs
        "plan", "meal plan", "eating plan", "diet plan", "nutrition plan",
        "program", "routine", "schedule", "daily plan",
        "suggested meals", "meal suggestions",
        
        # Recommendations
        "recommendation", "recommendations", "recommend", "recommends",
        "suggestion", "suggestions", "suggest", "suggests", "suggested",
        "advice", "tips for me",
        
        # Preferences & habits
        "preference", "preferences", "dietary restrictions", "allergies",
        "vegetarian", "vegan", "gluten free", "dairy free",
        "habit", "habits", "lifestyle", "routine",
        "picky eater", "don't like", "dislikes",
        
        # Flexibility
        "flexible", "flexibility", "rigid", "strict", "restrictive",
        "one size fits all", "generic", "same for everyone",
        
        # Common phrases
        "works for me", "doesn't fit", "not right for me",
        "takes into account", "considers my", "based on my"
    ],

    "Cost/Value": [
        # Pricing terms
        "price", "pricing", "priced", "cost", "costs", "expensive", "pricey",
        "cheap", "affordable", "reasonably priced", "reasonable",
        
        # Value assessment
        "value", "worth", "worth it", "not worth", "good value", "poor value",
        "overpriced", "too expensive", "too much", "too costly",
        "great deal", "good deal", "steal", "bargain",
        
        # Subscription models
        "subscription", "subscribe", "plan", "membership",
        "monthly", "annual", "yearly", "quarterly",
        "tier", "package", "premium", "basic plan", "pro plan",
        
        # Payments
        "fee", "fees", "paid", "pay", "paying", "charge", "charged", "charges",
        "money", "dollar", "bucks", "$", "payment", "billing",
        
        # Free vs paid
        "free", "free version", "free trial", "trial", "trial period",
        "upgrade", "upgraded", "downgrade",
        "premium features", "paywall", "locked", "requires payment",
        
        # Transactions
        "refund", "refunded", "cancel", "cancelled", "canceling", "cancellation",
        "renew", "renewal", "auto-renew", "charged again",
        
        # Comparisons
        "compared to", "vs", "versus", "other apps", "competitors",
        "alternatives", "cheaper alternative",
        
        # Common phrases
        "wish it was free", "would pay for", "not willing to pay",
        "waste of money", "best investment", "can't afford",
        "hidden costs", "hidden fees", "surprise charge"
    ],

    "Usability/Technical": [
        # Bugs & errors
        "bug", "bugs", "buggy", "glitch", "glitches", "glitchy",
        "error", "errors", "problem", "problems", "issue", "issues",
        "broken", "doesn't work", "not working", "won't work", "stopped working",
        
        # Performance
        "slow", "lag", "laggy", "lagging", "freeze", "freezes", "frozen",
        "crash", "crashes", "crashed", "crashing",
        "hang", "hangs", "stuck", "unresponsive",
        "load", "loading", "loads slowly", "won't load", "takes forever",
        
        # Updates
        "update", "updated", "updating", "new version", "latest version",
        "since the update", "after update", "broke after",
        
        # Design & interface
        "interface", "ui", "ux", "design", "layout", "look", "appearance",
        "menu", "navigation", "navigate", "find things",
        "cluttered", "clean", "organized", "messy", "confusing layout",
        
        # Usability
        "user friendly", "easy to use", "intuitive", "simple",
        "difficult", "hard to use", "complicated", "confusing",
        "learning curve", "figure out", "not obvious",
        "straightforward", "clear", "unclear",
        
        # Functionality
        "works", "working", "functional", "functions",
        "feature", "features", "tool", "tools", "function",
        "fix", "fixed", "needs fixing", "repair",
        
        # Connectivity
        "sync", "syncing", "syncs", "synchronize",
        "connection", "connect", "disconnect", "offline",
        "bluetooth", "wifi", "internet", "network",
        
        # Account/login
        "login", "log in", "sign in", "password", "username",
        "account", "profile", "forgot password", "locked out",
        "can't access", "won't let me",
        
        # Device compatibility
        "android", "ios", "iphone", "samsung", "phone",
        "tablet", "ipad", "device", "watch", "apple watch", "fitbit",
        
        # Common phrases
        "keeps crashing", "always freezing", "so buggy",
        "clunky", "smooth", "seamless", "frustrating",
        "wish it was easier", "hard to navigate"
    ]
}

def split_into_clauses(text):
    """
    Splits a review into smaller parts ("clauses") at words like but, however, etc.,
    so that mixed opinions in one sentence are analyzed separately.
    (This function was provided in the instructions)
    """
    # Split on connectors that often introduce new opinions
    parts = re.split(r'\b(?:but|however|although|though|while|and yet|whereas|nevertheless)\b', text, flags=re.IGNORECASE)
    # Clean and return non-empty clauses
    clauses = [p.strip() for p in parts if len(p.strip()) > 3] # Only keep clauses with more than 3 chars
    return clauses

def assign_bucket(clause):
    """
    Checks a clause for keywords and assigns it to one of the five feature buckets.
    Returns "Other" if no feature is detected.
    """
    # Make sure clause is string
    if not isinstance(clause, str):
        return "Other"
        
    # Iterate through our keyword dictionary
    # We return the *first* bucket that matches.
    for bucket, keywords in BUCKET_KEYWORDS.items():
        for keyword in keywords:
            # Simple check. Since text is already cleaned/lowercased, this is effective.
            if keyword in clause:
                return bucket
    # If no keywords are found in any bucket
    return "Other"

# -----------------------------------------------
# STEP 3: SENTIMENT CLASSIFICATION
# -----------------------------------------------

def analyze_sentiment(input_df, text_column):
    """
    Runs the full analysis pipeline:
    1. Loads the sentiment model
    2. Processes all reviews, sentences, and clauses
    3. Assigns buckets
    4. Runs sentiment analysis on bucketed clauses
    5. Returns a DataFrame with all results
    """
    
    print("Loading sentiment analysis model... (This may take a moment)")
    # Load the specific model requested
    try:
        sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure you have an internet connection and 'transformers' is installed.")
        print("Install it with: pip install transformers")
        return None

    print("Model loaded. Starting review processing...")
    
    # This list will store a dictionary for every clause we analyze
    all_clauses = []

    # Ensure the text column has no NaN values
    input_df[text_column] = input_df[text_column].fillna('')

    # Use tqdm for a progress bar as requested
    for review in tqdm(input_df[text_column], desc="Analyzing Reviews"):
        # 1. Split review into sentences
        sentences = sent_tokenize(review)
        
        for sentence in sentences:
            # 2. Split sentence into clauses
            clauses = split_into_clauses(sentence)
            
            for clause in clauses:
                # 3. Assign a bucket to the clause
                bucket = assign_bucket(clause)
                
                # 4. If it's a bucket we care about, analyze it
                if bucket != "Other":
                    try:
                        # Run the model
                        # The [0] is because the pipeline returns a list
                        result = sentiment_pipeline(clause)[0]
                        
                        # Store the results
                        all_clauses.append({
                            'clause': clause,
                            'bucket': bucket,
                            'label': result['label'],
                            'confidence': result['score']
                        })
                    except Exception as e:
                        print(f"Error processing clause: {clause}\nError: {e}")

    print(f"Processing complete. Found {len(all_clauses)} relevant clauses.")
    
    if not all_clauses:
        print("No relevant clauses were found with the current keywords. Cannot proceed.")
        return None

    # Convert the list of results into a DataFrame
    sent_df = pd.DataFrame(all_clauses)
    return sent_df

def plot_confidence_histogram(sent_df):
    """Plots the confidence histogram as requested."""
    if sent_df is None:
        return
        
    print("\nDisplaying model confidence histogram...")
    plt.figure(figsize=(10, 6))
    sent_df["confidence"].hist(bins=20, edgecolor='black')
    plt.title('Sentiment Model Confidence Distribution')
    plt.xlabel('Confidence Score')
    plt.ylabel('Number of Clauses')
    plt.grid(axis='y')
    plt.show()

# -----------------------------------------------
# STEP 4: AGGREGATION & PLOTTING
# -----------------------------------------------

def aggregate_and_plot_results(sent_df):
    """
    Aggregates the sentiment data by bucket and plots the final
    horizontal bar chart.
    """
    if sent_df is None:
        return

    print("\n--- Aggregated Sentiment Report ---")
    
    # Use groupby().value_counts() and unstack() as suggested
    sentiment_counts = sent_df.groupby('bucket')['label'].value_counts().unstack(fill_value=0)

    # Ensure both POSITIVE and NEGATIVE columns exist even if no clauses were found
    if 'POSITIVE' not in sentiment_counts.columns:
        sentiment_counts['POSITIVE'] = 0
    if 'NEGATIVE' not in sentiment_counts.columns:
        sentiment_counts['NEGATIVE'] = 0

    # Calculate metrics as requested
    sentiment_counts['total'] = sentiment_counts['POSITIVE'] + sentiment_counts['NEGATIVE']
    sentiment_counts['positive_rate'] = sentiment_counts['POSITIVE'] / sentiment_counts['total']
    sentiment_counts['negative_rate'] = sentiment_counts['NEGATIVE'] / sentiment_counts['total']
    
    # This is the final score
    sentiment_counts['sentiment_score'] = sentiment_counts['positive_rate'] - sentiment_counts['negative_rate']

    # Sort by the final score for a cleaner chart
    sentiment_counts = sentiment_counts.sort_values(by='sentiment_score', ascending=True)

    # Print the final table to the console
    print(sentiment_counts)
    print("-----------------------------------")

    # --- Create Bar Chart ---
    print("Displaying final sentiment score by feature...")
    
    scores = sentiment_counts['sentiment_score']
    # Create a color list: green for positive, red for negative
    colors = ['#4CAF50' if x >= 0 else '#F44336' for x in scores]
    
    plt.figure(figsize=(12, 8))
    scores.plot(kind='barh', color=colors, width=0.8)
    
    plt.title(f'Feature-Specific Sentiment Analysis ({CLEANED_INPUT_FILE})', fontsize=16)
    plt.xlabel('Sentiment Score (Positive Rate - Negative Rate)', fontsize=12)
    plt.ylabel('Feature Bucket', fontsize=12)
    
    # Add a vertical line at 0 for reference
    plt.axvline(x=0, color='grey', linestyle='--', linewidth=1)
    
    # Add grid lines for readability
    plt.grid(axis='x', linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.show()

# -----------------------------------------------
# MAIN EXECUTION
# -----------------------------------------------
if __name__ == "__main__":
    start_time = time.time()
    
    try:
        main_df = pd.read_csv(CLEANED_INPUT_FILE)
        print(f"Successfully loaded {len(main_df)} cleaned reviews from {CLEANED_INPUT_FILE}.")
        
        # Run the full analysis
        sentiment_results_df = analyze_sentiment(main_df, TEXT_COLUMN)
        
        if sentiment_results_df is not None:
            # Show the confidence histogram
            plot_confidence_histogram(sentiment_results_df)
            
            # Show the final aggregation and bar chart
            aggregate_and_plot_results(sentiment_results_df)
            
            # Save the raw clause data for further inspection
            sentiment_results_df.to_csv("noom_clause_level_sentiment.csv", index=False)
            print(f"\nSaved raw clause-level results to 'noom_clause_level_sentiment.csv'")

    except FileNotFoundError:
        print(f"Error: Input file '{CLEANED_INPUT_FILE}' not found.")
        print(f"Please run 'clean_fast_v2.py' first to generate this file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    end_time = time.time()
    print(f"\nTotal analysis time: {end_time - start_time:.2f} seconds")