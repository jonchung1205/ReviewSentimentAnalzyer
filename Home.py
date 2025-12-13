import streamlit as st

# ---------- Theme Colors ----------
# Using your existing palette, but adding a neutral gray for borders
PRIMARY = "#38577F"   
ACCENT = "#4670A4"    
LIGHT_BG = "#F8F9FA"  # Very light gray for the hero background
BORDER_COLOR = "#E6E9EF"

# ---------- Page Config ----------
st.set_page_config(
    page_title="Sentiment Analysis Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Custom CSS Styling ----------
st.markdown(
    f"""
    <style>
        /* Global Font Styling */
        .stApp {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        /* Main Title */
        .main-title {{
            font-size: 3rem;
            font-weight: 800;
            color: {PRIMARY};
            margin-bottom: 0;
            letter-spacing: -0.5px;
        }}

        .subtitle {{
            font-size: 1.2rem;
            font-weight: 400;
            color: #555;
            margin-top: 5px;
            margin-bottom: 30px;
        }}

        /* Hero / Info Box */
        .hero-container {{
            background-color: {LIGHT_BG};
            padding: 25px;
            border-radius: 8px;
            border-left: 5px solid {PRIMARY};
            color: #333;
            font-size: 1.05rem;
            line-height: 1.6;
            margin-bottom: 30px;
        }}

        /* Card Styling for Features */
        .feature-card {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid {BORDER_COLOR};
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            height: 100%; /* Ensures cards in the same row are equal height */
            transition: all 0.2s ease-in-out;
        }}

        .feature-card:hover {{
            border-color: {ACCENT};
            box-shadow: 0 6px 12px rgba(0,0,0,0.08);
            transform: translateY(-2px);
        }}

        .card-header {{
            color: {PRIMARY};
            font-weight: 700;
            font-size: 1.2rem;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 2px solid {LIGHT_BG};
        }}

        .card-text {{
            color: #4A4A4A;
            font-size: 0.95rem;
            line-height: 1.5;
        }}

        /* Badge for "Step 1, Step 2" */
        .step-badge {{
            background-color: {PRIMARY};
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.8rem;
            margin-bottom: 8px;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Hero Section ----------
st.markdown("<div class='main-title'>Sentiment Analysis Platform</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Unified scraping, pipeline execution, and data-driven insights</div>", unsafe_allow_html=True)

# ---------- Overview Box (Hero) ----------
st.markdown(
    f"""
    <div class="hero-container">
        This web app transforms backend scraping and sentiment analysis scripts into a single, 
        user-friendly interface. Built with Streamlit, it facilitates the collection,
        analysis, and visualization of user feedback directly from the <strong>App Store</strong> and <strong>Google Play Store</strong>.
    </div>
    """,
    unsafe_allow_html=True
)

st.write("") # Vertical spacer

# ---------- Features Grid ----------
st.markdown(f"<h3 style='color:{ACCENT}; border-bottom: 1px solid {BORDER_COLOR}; padding-bottom:10px;'>Platform Capabilities</h3>", unsafe_allow_html=True)
st.write("") 

# Create a 2x2 Grid Layout
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# Card 1: Scraping
with row1_col1:
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="card-header">Scrape Reviews</div>
            <div class="card-text">
                Connect to Google Play or App Store APIs. Run live review scraping for any target application set instantly.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with row1_col2:
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="card-header">Primitive Sentiment Analysis</div>
            <div class="card-text">
                Utilize the DistilBERT-powered pipeline to classify raw text sentiment and generate confidence scores.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Add spacing between rows
st.markdown("<br>", unsafe_allow_html=True)

# Card 3: Feature Analysis
with row2_col1:
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="card-header">Feature-Specific Sentiment</div>
            <div class="card-text">
                Granular analysis by category: Coaching, Logging, Personalization, Engagement, and UX.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with row2_col2:
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="card-header">Downloadable Outputs</div>
            <div class="card-text">
                Export cleaned datasets, labeled reviews, and summaries to CSV or Excel for external reporting.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# ---------- Getting Started ----------
st.markdown(f"<h3 style='color:{ACCENT}'>Workflow</h3>", unsafe_allow_html=True)
st.write("Use the sidebar navigation to execute the following steps:")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
        <div style="padding:10px;">
            <span class="step-badge">Step 1</span>
            <div style="font-weight:bold; color:{PRIMARY};">Scraper Tool</div>
            <div style="font-size:0.9rem; color:#666;">Fetch raw data.</div>
        </div>
        """, unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div style="padding:10px;">
            <span class="step-badge">Step 2</span>
            <div style="font-weight:bold; color:{PRIMARY};">Sentiment Analysis</div>
            <div style="font-size:0.9rem; color:#666;">Run either high level classification or feature specific sentiment analysis.</div>
        </div>
        """, unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div style="padding:10px;">
            <span class="step-badge">Step 3</span>
            <div style="font-weight:bold; color:{PRIMARY};">Interpret Results</div>
            <div style="font-size:0.9rem; color:#666;">Analyze exported files, plots, distribution scores.</div>
        </div>
        """, unsafe_allow_html=True
    )