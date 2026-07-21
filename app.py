import streamlit as st
import pickle
import requests
import time
import os

# -----------------------------
# Load Data
# -----------------------------
def download_file(url, filename):

    if not os.path.exists(filename):
        response = requests.get(url)

        with open(filename, "wb") as file:
            file.write(response.content)


movies_url = "https://huggingface.co/datasets/LIKITHASHREESR/movie-recommender-files/resolve/main/movies.pkl?download=true"

similarity_url = "https://huggingface.co/datasets/LIKITHASHREESR/movie-recommender-files/resolve/main/similarity.pkl?download=true"


download_file(movies_url, "movies.pkl")
download_file(similarity_url, "similarity.pkl")


movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

movie_titles = movies["title"].values

# -----------------------------
# TMDB API Key
# -----------------------------
API_KEY = st.secrets["TMDB_API_KEY"]   # Replace with your API key

# -----------------------------
# Fetch Movie Poster
# -----------------------------
session = requests.Session()

@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    for attempt in range(3):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            poster_path = data.get("poster_path")

            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
            else:
                return "https://via.placeholder.com/500x750?text=No+Poster"

        except requests.exceptions.RequestException:
            time.sleep(1)

    return "https://via.placeholder.com/500x750?text=No+Poster"

# -----------------------------
# Recommendation Function
# -----------------------------
def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for item in movie_list:
        movie_id = movies.iloc[item[0]].movie_id
        recommended_movies.append(movies.iloc[item[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "Choose a movie",
    movie_titles
)

if st.button("Recommend"):

    names, posters = recommend(selected_movie)

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.markdown(f"**{names[i]}**")