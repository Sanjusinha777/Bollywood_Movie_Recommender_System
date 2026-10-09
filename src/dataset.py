"""
Dataset manager and search index for Bollywood movies.
Handles loading, fuzzy searching, acronym resolution, and metadata formatting.
"""

import os
import re
import difflib
import pandas as pd
from typing import List, Dict, Optional, Tuple

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bollywood_movies.csv")

# Famous Bollywood acronyms and aliases
COMMON_ALIASES = {
    "ddlj": "Dilwale Dulhania Le Jayenge",
    "k3g": "Kabhi Khushi Kabhie Gham...",
    "znmd": "Zindagi Na Milegi Dobara",
    "yjhd": "Yeh Jawaani Hai Deewani",
    "gow": "Gangs of Wasseypur",
    "khnh": "Kal Ho Naa Ho",
    "dch": "Dil Chahta Hai",
    "rdb": "Rang De Basanti",
    "kkhh": "Kuch Kuch Hota Hai",
    "haphk": "Hum Aapke Hain Koun..!",
    "hddd": "Hum Dil De Chuke Sanam",
    "mbbs": "Munna Bhai M.B.B.S.",
    "3 idiots": "3 Idiots",
    "3 idiot": "3 Idiots",
    "idiots": "3 Idiots",
    "ms dhoni": "M.S. Dhoni: The Untold Story",
    "msdhoni": "M.S. Dhoni: The Untold Story",
    "tzp": "Taare Zameen Par",
    "krrish 3": "Krrish 3",
    "bb2": "Bhool Bhulaiyaa 2",
    "bb3": "Bhool Bhulaiyaa 3",
    "omg": "OMG: Oh My God!",
    "omg 2": "OMG 2",
    "stree 2": "Stree 2",
    "12 fail": "12th Fail",
    "twelfth fail": "12th Fail",
    "pk": "PK"
}


class BollywoodDataset:
    def __init__(self, csv_path: str = DATA_FILE):
        self.csv_path = csv_path
        self.df: pd.DataFrame = pd.DataFrame()
        self.titles: List[str] = []
        self._lower_title_map: Dict[str, str] = {}
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.csv_path):
            # Attempt to trigger build if missing
            from build_dataset import build_unified_dataset
            self.df = build_unified_dataset()
        else:
            self.df = pd.read_csv(self.csv_path)

        # Clean title text and remove unicode replacement artifacts
        def clean_entry_title(t):
            t = str(t).replace("\ufffd", "").replace("–", "-").replace("—", "-")
            # Remove any double spaces
            t = re.sub(r"\s+", " ", t).strip()
            return t

        self.df["title"] = self.df["title"].fillna("").apply(clean_entry_title)
        
        # Filter out invalid, untitled, or placeholder rows
        mask_valid = (
            (self.df["title"].str.len() >= 2) &
            (~self.df["title"].str.lower().str.startswith("untitled")) &
            (~self.df["title"].str.lower().str.contains("untitled project|untitled film|untitled movie", regex=True))
        )
        self.df = self.df[mask_valid].reset_index(drop=True)

        # Fill any null values
        self.df["year"] = pd.to_numeric(self.df["year"], errors="coerce").fillna(2000).astype(int)
        self.df["genre"] = self.df["genre"].fillna("Drama, Bollywood").astype(str)
        self.df["director"] = self.df["director"].fillna("Bollywood Director").astype(str)
        self.df["actors"] = self.df["actors"].fillna("Ensemble Cast").astype(str)
        self.df["overview"] = self.df["overview"].fillna("A classic Bollywood film.").astype(str)
        self.df["imdb_rating"] = pd.to_numeric(self.df["imdb_rating"], errors="coerce").fillna(7.0).round(1)
        self.df["poster_path"] = self.df["poster_path"].fillna("").astype(str)

        self.titles = self.df["title"].tolist()
        self._lower_title_map = {t.lower().strip(): t for t in self.titles}

    def get_all_titles(self) -> List[str]:
        return sorted(list(set(self.titles)), key=lambda x: x.lower())

    def search_movie(self, query: str) -> Optional[str]:
        """
        Finds the closest canonical movie title matching the user query.
        Handles exact matches, acronyms, substrings, and fuzzy matching.
        """
        if not query or not query.strip():
            return None

        clean_q = query.strip().lower()

        # Check aliases
        if clean_q in COMMON_ALIASES:
            alias_target = COMMON_ALIASES[clean_q]
            if alias_target in self.titles:
                return alias_target
            # Try fuzzy match on alias target
            matches = difflib.get_close_matches(alias_target, self.titles, n=1, cutoff=0.6)
            if matches:
                return matches[0]

        # Exact case-insensitive match
        if clean_q in self._lower_title_map:
            return self._lower_title_map[clean_q]

        # Substring exact match (e.g., query 'zindagi na milegi' matches 'Zindagi Na Milegi Dobara')
        substring_matches = [t for t in self.titles if clean_q in t.lower()]
        if substring_matches:
            # Sort by length similarity
            substring_matches.sort(key=lambda t: abs(len(t) - len(clean_q)))
            return substring_matches[0]

        # Normalized alphanumeric match (ignores punctuation like colons, hyphens)
        alpha_q = re.sub(r"[^\w\s]", "", clean_q).strip()
        for t in self.titles:
            alpha_t = re.sub(r"[^\w\s]", "", t.lower()).strip()
            if alpha_q == alpha_t or alpha_q in alpha_t:
                return t

        # Fuzzy string matching with difflib
        fuzzy_matches = difflib.get_close_matches(query.strip(), self.titles, n=3, cutoff=0.5)
        if fuzzy_matches:
            return fuzzy_matches[0]

        # Lowercase fuzzy matching
        lower_fuzzy = difflib.get_close_matches(clean_q, list(self._lower_title_map.keys()), n=1, cutoff=0.45)
        if lower_fuzzy:
            return self._lower_title_map[lower_fuzzy[0]]

        return None

    def get_movie_details(self, title: str) -> Optional[Dict]:
        """Returns metadata dictionary for a movie title."""
        matched = self.df[self.df["title"] == title]
        if matched.empty:
            # Try case-insensitive
            matched = self.df[self.df["title"].str.lower() == title.lower()]
        if matched.empty:
            return None

        row = matched.iloc[0]
        return {
            "title": str(row["title"]),
            "year": int(row["year"]),
            "genre": str(row["genre"]),
            "director": str(row["director"]),
            "actors": str(row["actors"]),
            "overview": str(row["overview"]),
            "imdb_rating": float(row["imdb_rating"]),
            "poster_path": str(row["poster_path"])
        }

    def get_top_rated(self, limit: int = 10) -> List[Dict]:
        """Returns top rated Bollywood movies."""
        top_df = self.df.sort_values(by=["imdb_rating", "year"], ascending=[False, False]).head(limit)
        return top_df.to_dict(orient="records")

    def get_by_era(self, era: str) -> pd.DataFrame:
        """Filter movies by era."""
        if era == "Golden Age (1950-1979)":
            return self.df[(self.df["year"] >= 1950) & (self.df["year"] <= 1979)]
        elif era == "Classic & 90s (1980-1999)":
            return self.df[(self.df["year"] >= 1980) & (self.df["year"] <= 1999)]
        elif era == "Millennium (2000-2009)":
            return self.df[(self.df["year"] >= 2000) & (self.df["year"] <= 2009)]
        elif era == "Modern Wave (2010-2019)":
            return self.df[(self.df["year"] >= 2010) & (self.df["year"] <= 2019)]
        elif era == "Recent Hits (2020-Present)":
            return self.df[self.df["year"] >= 2020]
        return self.df
