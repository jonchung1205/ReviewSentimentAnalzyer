# -------------------------
# Environment setup
# -------------------------
import nltk
import pandas as pd
import emoji
import string
import re
import unicodedata
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# -------------------------
# Text cleaning function
# -------------------------
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    """
    Cleans text data for NLP analysis using a robust pipeline.
    Steps include: lowercasing, emoji removal, symbol/punctuation removal,
    stop word removal, and lemmatization.
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove Emojis using the dedicated 'emoji' library
    text = emoji.replace_emoji(text, replace='')
    
    # 3. Remove Punctuation and Symbols (More Robust than simple regex)
    # This keeps only characters that are Letters or Numbers (L or N) and Whitespace (Z)
    cleaned_chars = []
    for char in text:
        category = unicodedata.category(char)
        # Keep letters (L), numbers (N), and spaces/separators (Z)
        if category.startswith(('L', 'N')) or category.startswith('Z'):
            cleaned_chars.append(char)

    text = ''.join(cleaned_chars)
    
    # 4. Normalize Whitespace (replace multiple spaces with a single one)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 5. Tokenize
    words = text.split()
    
    # 6. Remove Stopwords and Lemmatize
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    
    return ' '.join(words)

# -------------------------
# Apply cleaning to CSV
# -------------------------
if __name__ == "__main__":
    print(f"Starting data cleaning process on {INPUT_FILE}...")
    
    # Define the metadata columns you want to keep (uncleaned)
    METADATA_COLUMNS = ['date'] 
    
    # Define ALL text columns that require cleaning
    TEXT_COLUMNS_TO_CLEAN = ['content', 'title', 'user_name']

    try:
        # Load scraped data
        df = pd.read_csv(INPUT_FILE)

        # Apply cleaning process
        for col in TEXT_COLUMNS_TO_CLEAN:
            cleaned_col_name = f'cleaned_{col}'

            if col not in df.columns:
                print(f"Warning: The CSV file is missing the column '{col}'. Skipping cleaning for this column.")
                continue

            # Fill NaN values with empty string before cleaning
            df[col] = df[col].fillna('')

            # Clean the column and store result in a new column
            df[cleaned_col_name] = df[col].apply(clean_text)
            
        # Ensure metadata columns exist, but only to warn if missing
        for meta_col in METADATA_COLUMNS:
            if meta_col not in df.columns:
                 print(f"Warning: Metadata column '{meta_col}' not found in the input file. It will be skipped.")

        # --- KEY CHANGE: Define the strict output order and filter for existence ---
        
        # 1. Define the strict, desired output column order
        DESIRED_FINAL_ORDER = [
            'date',
            'cleaned_user_name', # <-- Now correctly placed second
            'cleaned_content',
            'cleaned_title'
        ]

        # 2. Filter this list to include only columns that actually exist in the DataFrame (df).
        # This handles cases where original columns were missing and thus the cleaned columns were not created.
        FINAL_OUTPUT_COLUMNS = [col for col in DESIRED_FINAL_ORDER if col in df.columns]


        # Select the columns in the desired order
        df_cleaned = df[FINAL_OUTPUT_COLUMNS]

        # Save cleaned data
        df_cleaned.to_csv(OUTPUT_FILE, index=False)
        print(f"Data cleaning complete. Ordered columns saved as {OUTPUT_FILE}")
        print(f"Final column order: {FINAL_OUTPUT_COLUMNS}")

    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found. Please check the file path.")
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}")