"""
Recommendation Engine for Bollywood Movies.
Implements content-based filtering using an enriched metadata soup (director,
cast, genres, plot overview, and era) with TF-IDF vectorization and Cosine Similarity,
plus explainable recommendation highlights.
"""

import re
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.dataset import BollywoodDataset
from src.poster_fetcher import get_poster_url


def clean_entity(name: str) -> str:
    """Collapses entity names to single tokens, e.g. 'Shah Rukh Khan' -> 'shahrukhkhan'."""
    if not isinstance(name, str):
        return ""
    # Strip spaces and punctuation
    cleaned = re.sub(r"[^\w]", "", name.lower())
    return cleaned


def get_era_token(year: int) -> str:
    if year < 1980:
        return "era_golden_classics"
    elif year < 1990:
        return "era_eighties_action"
    elif year < 2000:
        return "era_nineties_romance"
    elif year < 2010:
        return "era_millennium_wave"
    elif year < 2020:
        return "era_modern_cinema"
    else:
        return "era_contemporary_blockbuster"


class BollywoodRecommender:
    def __init__(self, dataset: Optional[BollywoodDataset] = None):
        self.dataset = dataset if dataset is not None else BollywoodDataset()
        self.df = self.dataset.df
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.build_index()

    def _create_metadata_soup(self, row: pd.Series) -> str:
        """
        Creates a weighted metadata representation for content-based similarity.
        - Directors: 3x weight
        - Key Cast: 2x weight
        - Genres: 2x weight
        - Era token: 1x weight
        - Overview / Plot keywords: 1x weight
        """
        title = str(row.get("title", ""))
        overview = str(row.get("overview", "")).lower()

        # Directors
        director_raw = str(row.get("director", ""))
        directors = [clean_entity(d.strip()) for d in re.split(r"[,/|;]", director_raw) if len(d.strip()) > 1]
        directors_token = " ".join([f"dir_{d}" for d in directors if d])
        directors_weighted = f"{directors_token} {directors_token} {directors_token}"

        # Actors
        actors_raw = str(row.get("actors", ""))
        actors = [clean_entity(a.strip()) for a in re.split(r"[,/|;]", actors_raw) if len(a.strip()) > 1][:5]
        actors_token = " ".join([f"actor_{a}" for a in actors if a])
        actors_weighted = f"{actors_token} {actors_token}"

        # Genres
        genres_raw = str(row.get("genre", ""))
        genres = [clean_entity(g.strip()) for g in re.split(r"[,/|;]", genres_raw) if len(g.strip()) > 1]
        genres_token = " ".join([f"genre_{g}" for g in genres if g])
        genres_weighted = f"{genres_token} {genres_token}"

        # Era
        year = int(row.get("year", 2000))
        era = get_era_token(year)

        # Overview cleaning
        clean_overview = re.sub(r"[^\w\s]", " ", overview)

        soup = f"{genres_weighted} {directors_weighted} {actors_weighted} {era} {clean_overview}"
        return soup

    def build_index(self):
        """Constructs the TF-IDF feature space."""
        print(f"Building recommendation index for {len(self.df)} Bollywood movies...")
        soups = self.df.apply(self._create_metadata_soup, axis=1)

        self.vectorizer = TfidfVectorizer(
            max_features=15000,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(soups)
        print("Recommendation index successfully built!")

    def explain_similarity(self, source_row: pd.Series, target_row: pd.Series) -> List[str]:
        """Generates human-readable reasons why target movie was recommended for source movie."""
        reasons = []

        # Check Director overlap
        d1 = {clean_entity(d.strip()) for d in re.split(r"[,/|;]", str(source_row.get("director", ""))) if len(d.strip()) > 1}
        d2 = {clean_entity(d.strip()) for d in re.split(r"[,/|;]", str(target_row.get("director", ""))) if len(d.strip()) > 1}
        shared_directors = d1.intersection(d2)
        if shared_directors and "" not in shared_directors:
            reasons.append(f"Directed by {target_row.get('director')}")

        # Check Actor overlap
        a1 = {clean_entity(a.strip()) for a in re.split(r"[,/|;]", str(source_row.get("actors", ""))) if len(a.strip()) > 1}
        a2 = {clean_entity(a.strip()) for a in re.split(r"[,/|;]", str(target_row.get("actors", ""))) if len(a.strip()) > 1}
        shared_actors = a1.intersection(a2)
        if shared_actors:
            # Find pretty names
            actor_names = []
            for raw_a in re.split(r"[,/|;]", str(target_row.get("actors", ""))):
                if clean_entity(raw_a) in shared_actors:
                    actor_names.append(raw_a.strip())
            if actor_names:
                reasons.append(f"Starring {', '.join(actor_names[:2])}")

        # Check Genre overlap
        g1 = {g.strip().lower() for g in re.split(r"[,/|;]", str(source_row.get("genre", ""))) if len(g.strip()) > 1}
        g2 = {g.strip().lower() for g in re.split(r"[,/|;]", str(target_row.get("genre", ""))) if len(g.strip()) > 1}
        shared_genres = g1.intersection(g2)
        if shared_genres:
            cap_genres = [g.capitalize() for g in list(shared_genres)[:2]]
            reasons.append(f"Shared genres: {', '.join(cap_genres)}")

        # Same Era
        y1 = int(source_row.get("year", 2000))
        y2 = int(target_row.get("year", 2000))
        if abs(y1 - y2) <= 3:
            reasons.append(f"Released in the same era ({y2})")

        if not reasons:
            reasons.append("Similar thematic storyline and cinema style")

        return reasons[:3]

    def recommend(self, query: str, top_k: int = 5) -> Tuple[Optional[Dict], List[Dict]]:
        """
        Takes a movie search query, finds the best match,
        and returns (source_movie_details, list_of_top_k_recommendations).
        """
        # Resolve movie title
        canonical_title = self.dataset.search_movie(query)
        if not canonical_title:
            return None, []

        # Find positional index in dataframe
        matches = np.where(self.df["title"].values == canonical_title)[0]
        if len(matches) == 0:
            return None, []

        query_idx = int(matches[0])
        source_row = self.df.iloc[query_idx]

        # Compute cosine similarity between the query movie and all other movies
        query_vector = self.tfidf_matrix[query_idx]
        sim_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        # Sort indices by similarity score descending
        ranked_indices = np.argsort(sim_scores)[::-1]

        # Exclude self and pick top_k
        recommendations = []
        for idx in ranked_indices:
            if idx == query_idx:
                continue

            target_row = self.df.iloc[idx]
            raw_score = float(sim_scores[idx])

            # Normalize to human percentage (boost low cosine range for friendly display)
            # Typically TF-IDF cosine similarity runs in [0.05, 0.6] range
            pct_score = min(99, max(65, int(50 + (raw_score * 80))))

            poster_url = get_poster_url(
                str(target_row.get("poster_path", "")),
                str(target_row.get("title", "")),
                str(target_row.get("genre", "")),
                int(target_row.get("year", 2000)),
                float(target_row.get("imdb_rating", 7.0))
            )

            reasons = self.explain_similarity(source_row, target_row)

            rec_item = {
                "title": str(target_row.get("title", "")),
                "year": int(target_row.get("year", 2000)),
                "genre": str(target_row.get("genre", "")),
                "director": str(target_row.get("director", "")),
                "actors": str(target_row.get("actors", "")),
                "overview": str(target_row.get("overview", "")),
                "imdb_rating": float(target_row.get("imdb_rating", 7.0)),
                "poster_path": poster_url,
                "similarity_score": f"{pct_score}%",
                "raw_score": round(raw_score, 4),
                "reasons": reasons
            }
            recommendations.append(rec_item)

            if len(recommendations) >= top_k:
                break

        # Source movie details
        source_details = {
            "title": str(source_row.get("title", "")),
            "year": int(source_row.get("year", 2000)),
            "genre": str(source_row.get("genre", "")),
            "director": str(source_row.get("director", "")),
            "actors": str(source_row.get("actors", "")),
            "overview": str(source_row.get("overview", "")),
            "imdb_rating": float(source_row.get("imdb_rating", 7.0)),
            "poster_path": get_poster_url(
                str(source_row.get("poster_path", "")),
                str(source_row.get("title", "")),
                str(source_row.get("genre", "")),
                int(source_row.get("year", 2000)),
                float(source_row.get("imdb_rating", 7.0))
            )
        }

        return source_details, recommendations
