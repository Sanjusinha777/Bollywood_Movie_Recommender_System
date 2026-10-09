"""
Streamlit Web Application for Bollywood Movie Recommender System.
A modern, cinematic interface providing content-based recommendations
for 4,900+ Bollywood movies across all eras of Indian cinema.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List

from src.dataset import BollywoodDataset
from src.engine import BollywoodRecommender

# Streamlit Page Configuration
st.set_page_config(
    page_title="Bollywood Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling: Cinematic Dark Theme with Gold & Crimson Highlights
CINEMA_CSS = """
<style>
    /* Global styling */
    .stApp {
        background: linear-gradient(135deg, #0b0c10 0%, #1f2833 50%, #0b0c10 100%);
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header hero */
    .hero-header {
        text-align: center;
        padding: 24px 10px 15px 10px;
        background: linear-gradient(90deg, rgba(229,9,20,0.15) 0%, rgba(245,166,35,0.15) 100%);
        border-radius: 12px;
        margin-bottom: 25px;
        border: 1px solid rgba(245,166,35,0.3);
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #ff4b2b, #ff416c, #ffb347);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    
    .hero-subtitle {
        font-size: 1.15rem;
        color: #cfd8dc;
        margin-bottom: 0px;
    }
    
    /* Movie Selected Banner */
    .selected-card {
        background: rgba(22, 27, 34, 0.95);
        border: 1px solid rgba(245, 166, 35, 0.4);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    /* Recommendation Cards */
    .rec-card {
        background: #161b22;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .rec-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 24px rgba(229, 9, 20, 0.35);
        border-color: rgba(245, 166, 35, 0.6);
    }
    
    /* High Definition Movie Poster Styling */
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 12px;
    }
    div[data-testid="stImage"] > img {
        border-radius: 10px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.65) !important;
        object-fit: cover !important;
        aspect-ratio: 2 / 3 !important;
        width: 100% !important;
        border: 1.5px solid rgba(245, 166, 35, 0.3) !important;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease, border-color 0.3s ease !important;
    }
    div[data-testid="stImage"] > img:hover {
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 16px 36px rgba(229, 9, 20, 0.5) !important;
        border-color: rgba(245, 166, 35, 0.85) !important;
    }
    
    .rec-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
        line-height: 1.3;
        min-height: 2.6rem;
    }
    
    .badge-match {
        display: inline-block;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 20px;
        margin-bottom: 8px;
    }
    
    .badge-rating {
        display: inline-block;
        background: #f59e0b;
        color: #111827;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 2px 7px;
        border-radius: 4px;
        margin-left: 6px;
    }
    
    .rec-meta {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-bottom: 4px;
    }
    
    .rec-reason {
        font-size: 0.75rem;
        color: #6ee7b7;
        background: rgba(16, 185, 129, 0.1);
        padding: 4px 6px;
        border-radius: 4px;
        margin-top: 6px;
        border-left: 2px solid #10b981;
    }
</style>
"""

st.markdown(CINEMA_CSS, unsafe_allow_html=True)


@st.cache_resource
def load_recommender():
    ds = BollywoodDataset()
    rec = BollywoodRecommender(ds)
    return ds, rec


ds, recommender = load_recommender()

# Hero Header
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🎬 Bollywood Movie Recommender</div>
    <div class="hero-subtitle">Search any Bollywood movie to discover <b>5 most similar Hindi films</b> powered by AI & Content Similarity</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=80", use_container_width=True)
    st.markdown("### 🍿 Cinema Control Room")
    st.markdown(f"**Database Size:** `{len(ds.df):,}` Hindi Movies")
    st.markdown(f"**Coverage:** `1950 – 2024` (74+ Years)")
    
    st.divider()
    
    st.markdown("#### ⚡ Popular Searches")
    popular_picks = [
        "3 Idiots",
        "Dilwale Dulhania Le Jayenge",
        "Sholay",
        "Zindagi Na Milegi Dobara",
        "Jawan",
        "Gangs of Wasseypur",
        "12th Fail",
        "Andhadhun",
        "Dangal",
        "Queen",
        "Munna Bhai M.B.B.S.",
        "Jab We Met"
    ]
    
    selected_quick_pick = None
    for pick in popular_picks:
        if st.button(f"🎬 {pick}", key=f"quick_{pick}", use_container_width=True):
            st.session_state["search_query"] = pick

    st.divider()
    st.info("💡 **Tip:** You can search by movie names, short acronyms like `DDLJ`, `ZNMD`, `K3G`, or directors like `Rajkumar Hirani`.")

# Search Input Section
all_titles = ds.get_all_titles()

col_search, col_btn = st.columns([4, 1])

if "search_query" not in st.session_state:
    st.session_state["search_query"] = "3 Idiots"

with col_search:
    search_input = st.text_input(
        "Search Bollywood Movie Title or Acronym (e.g., '3 Idiots', 'DDLJ', 'Sholay', 'Pathaan'):",
        value=st.session_state.get("search_query", "3 Idiots"),
        placeholder="Type a movie title, e.g., '3 Idiots' or 'DDLJ'..."
    )

with col_btn:
    st.write("")
    st.write("")
    trigger_search = st.button("🚀 Recommend", type="primary", use_container_width=True)

query_to_run = search_input.strip()

if query_to_run:
    source_movie, recommendations = recommender.recommend(query_to_run, top_k=5)

    if not source_movie:
        st.error(f"❌ Could not find a Bollywood movie matching '**{query_to_run}**'.")
        # Offer suggestions
        import difflib
        suggestions = difflib.get_close_matches(query_to_run, all_titles, n=5, cutoff=0.35)
        if suggestions:
            st.warning("🔍 Did you mean one of these?")
            cols = st.columns(len(suggestions))
            for i, sug in enumerate(suggestions):
                with cols[i]:
                    if st.button(sug, key=f"sug_{i}"):
                        st.session_state["search_query"] = sug
                        st.rerun()
    else:
        # Display Selected Movie Banner
        st.markdown(f"### 🎯 Selected Movie: **{source_movie['title']}** ({source_movie['year']})")
        
        banner_col1, banner_col2 = st.columns([1, 4])
        with banner_col1:
            st.image(source_movie["poster_path"], use_container_width=True)
        with banner_col2:
            st.markdown(f"""
            #### {source_movie['title']} <span class="badge-rating">⭐ {source_movie['imdb_rating']}/10</span>
            - **📅 Release Year:** `{source_movie['year']}`
            - **🎭 Genres:** `{source_movie['genre']}`
            - **🎬 Director:** `{source_movie['director']}`
            - **🌟 Key Cast:** `{source_movie['actors']}`
            - **📖 Storyline:** {source_movie['overview']}
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"### 🌟 Top 5 Similar Bollywood Movies For You")
        st.markdown(f"These 5 films share closely matched genres, cast, directorial vision, and narrative themes with **{source_movie['title']}**:")

        # 5 Columns for 5 Recommendations
        rec_cols = st.columns(5)

        for i, rec in enumerate(recommendations):
            with rec_cols[i]:
                # Poster Image
                st.image(rec["poster_path"], use_container_width=True)
                
                # Title and Year
                st.markdown(f"**{i+1}. {rec['title']}** ({rec['year']})")
                
                # Badges
                st.markdown(f"""
                <span class="badge-match">{rec['similarity_score']}</span>
                <span class="badge-rating">⭐ {rec['imdb_rating']}</span>
                """, unsafe_allow_html=True)
                
                # Details
                st.caption(f"🎭 **Genre:** {rec['genre']}")
                st.caption(f"🎬 **Director:** {rec['director']}")
                st.caption(f"🌟 **Cast:** {rec['actors'][:45]}...")
                
                # Recommendation rationale
                if rec.get("reasons"):
                    st.markdown(f"""<div class="rec-reason">💡 {rec['reasons'][0]}</div>""", unsafe_allow_html=True)
                
                # Expander for plot
                with st.expander("📖 Read Plot"):
                    st.write(rec["overview"])
                
                # Quick button to pivot search to this movie
                if st.button(f"🔍 Similar to this", key=f"rec_pivot_{i}_{rec['title']}"):
                    st.session_state["search_query"] = rec["title"]
                    st.rerun()

# Era Exploration Section
st.markdown("---")
with st.expander("🏛️ Explore Bollywood Cinema by Era"):
    era_choice = st.selectbox(
        "Select an Era to explore top films:",
        [
            "Recent Hits (2020-Present)",
            "Modern Wave (2010-2019)",
            "Millennium (2000-2009)",
            "Classic & 90s (1980-1999)",
            "Golden Age (1950-1979)"
        ]
    )
    era_df = ds.get_by_era(era_choice).sort_values(by=["imdb_rating"], ascending=False).head(10)
    st.dataframe(
        era_df[["title", "year", "genre", "director", "imdb_rating"]],
        use_container_width=True,
        hide_index=True
    )
