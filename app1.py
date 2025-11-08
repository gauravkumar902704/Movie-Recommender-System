import pickle
import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
from requests.exceptions import ConnectionError, Timeout

# ======================================================
# 🖌️ Page Configuration
# ======================================================
st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🎥", layout="wide")

# ======================================================
# 🌌 Custom Background & Theme
# ======================================================
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: linear-gradient(rgba(10,10,10,0.75), rgba(10,10,10,0.85)), 
                      url("https://i.ibb.co/jVpxtKh/cinema-bg.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: white;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

.css-1y4p8pa, .css-17lntkn {
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(8px);
    border-radius: 15px;
}

h1, h2, h3, h4, h5, h6, p, span, label {
    color: #f8f8f8 !important;
}

.stButton>button {
    background-color: #e50914;
    color: white;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    font-weight: bold;
    border: none;
    box-shadow: 0px 0px 10px rgba(229,9,20,0.5);
    transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
    background-color: #ff1a1a;
    transform: scale(1.05);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ======================================================
# 🎬 Fetch Poster Function
# ======================================================
def fetch_poster(movie_id, api_key):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        overview = data.get('overview', 'No description available.')
        rating = data.get('vote_average', 'N/A')
        release = data.get('release_date', 'Unknown')

        if poster_path:
            poster_url = "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            poster_url = "https://via.placeholder.com/500x750?text=No+Image"

        return poster_url, overview, rating, release

    except (ConnectionError, Timeout):
        print(f"⚠️ Connection issue for movie_id {movie_id}")
        return "https://via.placeholder.com/500x750?text=No+Image", "", "N/A", "Unknown"
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return "https://via.placeholder.com/500x750?text=Error", "", "N/A", "Unknown"

# ======================================================
# 🎥 Recommend Function
# ======================================================
def recommend(movie, api_key):
    if not isinstance(movies, pd.DataFrame):
        st.error("❌ 'movies' is not a DataFrame. Please check how it's loaded.")
        return [], [], [], [], []

    if 'title' not in movies.columns:
        st.error("❌ 'title' column missing in movies dataset.")
        return [], [], [], [], []

    if movie not in movies['title'].values:
        st.error(f"⚠️ Movie '{movie}' not found in dataset.")
        return [], [], [], [], []

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    rec_names, rec_posters, rec_overviews, rec_ratings, rec_release = [], [], [], [], []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        poster, overview, rating, release = fetch_poster(movie_id, api_key)
        rec_names.append(movies.iloc[i[0]].title)
        rec_posters.append(poster)
        rec_overviews.append(overview)
        rec_ratings.append(rating)
        rec_release.append(release)
        time.sleep(0.5)

    return rec_names, rec_posters, rec_overviews, rec_ratings, rec_release

# ======================================================
# 🌟 Streamlit UI
# ======================================================
st.markdown("<h1 style='text-align: center;'>🎞️ Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Find your next favorite movie with AI-powered recommendations 🍿</p>", unsafe_allow_html=True)

# Load pickled data
try:
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Sidebar settings
st.sidebar.header("⚙️ Settings")
api_key = st.sidebar.text_input("🔑 Enter your TMDb API Key:", 
                                value="8265bd1679663a7ea12ac168da84d2e8", 
                                type="password")
st.sidebar.markdown("[Get your free TMDb API key](https://www.themoviedb.org/settings/api)")
st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Use your own API key for faster, more reliable results.")

# Movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox("🎥 Select a Movie", movie_list)

# Recommendation button
if st.button('🍿 Show Recommendations'):
    with st.spinner('Fetching recommendations... Please wait...'):
        names, posters, overviews, ratings, release_dates = recommend(selected_movie, api_key)

    if names:
        st.markdown("### 🔥 Recommended Movies")
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i], use_container_width=True)
                st.markdown(f"<h4 style='text-align:center; color:#FF5555;'>{names[i]}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:13px; text-align:center;'>⭐ Rating: {ratings[i]}<br>📅 {release_dates[i]}</p>", unsafe_allow_html=True)
                with st.expander("📖 Overview"):
                    st.write(overviews[i])
    else:
        st.warning("No recommendations found or connection issue.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; font-size:14px; color:#aaaaaa;'>🎬 Built by Gaurav Kumar | Powered by Streamlit & TMDb API</p>", unsafe_allow_html=True)
