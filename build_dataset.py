"""
Dataset Builder for Bollywood Movie Recommender System.
Merges historical databases (1950-2019 TIMDB, 1951-2023 IMDB) and modern blockbusters
into a unified, deduplicated dataset with rich metadata.
"""

import os
import re
import urllib.request
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "bollywood_movies.csv")

URL_TIMDB = "https://raw.githubusercontent.com/pncnmnp/TIMDB/master/1950-2019/bollywood_full.csv"
URL_IMDB_2023 = "https://raw.githubusercontent.com/devensinghbhagtani/Bollywood-Movie-Dataset/main/IMDB-Movie-Dataset(2023-1951).csv"

# Essential landmark recent Bollywood movies to ensure complete coverage up to 2024
CURATED_MODERN_MOVIES = [
    {
        "title": "Jawan",
        "year": 2023,
        "genre": "Action, Thriller, Drama",
        "director": "Atlee",
        "actors": "Shah Rukh Khan, Nayanthara, Vijay Sethupathi, Deepika Padukone, Sanya Malhotra",
        "overview": "A high-octane action thriller outlining the emotional journey of a man who is set out to rectify the wrongs in the society and fight against corruption.",
        "imdb_rating": 7.0,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/3/39/Jawan_film_poster.jpg"
    },
    {
        "title": "Pathaan",
        "year": 2023,
        "genre": "Action, Thriller, Adventure",
        "director": "Siddharth Anand",
        "actors": "Shah Rukh Khan, Deepika Padukone, John Abraham, Dimple Kapadia, Salman Khan",
        "overview": "An Indian RAW agent teams up with an exiled spy to stop a rogue private terrorist organization led by Jim from unleashing a deadly viral weapon against India.",
        "imdb_rating": 5.9,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/c/c3/Pathaan_film_poster.jpg"
    },
    {
        "title": "Animal",
        "year": 2023,
        "genre": "Action, Crime, Drama",
        "director": "Sandeep Reddy Vanga",
        "actors": "Ranbir Kapoor, Anil Kapoor, Bobby Deol, Rashmika Mandanna, Triptii Dimri",
        "overview": "A violent, obsessive son undergoes a ferocious transformation to protect and avenge his estranged, emotionally unavailable father who survives an assassination attempt.",
        "imdb_rating": 6.1,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/9/90/Animal_%282023_film%29_poster.jpg"
    },
    {
        "title": "12th Fail",
        "year": 2023,
        "genre": "Biography, Drama",
        "director": "Vidhu Vinod Chopra",
        "actors": "Vikrant Massey, Medha Shankr, Anant V Joshi, Anshumaan Pushkar, Priyanshu Chatterjee",
        "overview": "Based on the inspiring real-life story of IPS officer Manoj Kumar Sharma who braves extreme poverty, failure, and hardships to clear the rigorous UPSC Civil Services examination.",
        "imdb_rating": 8.9,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/f/f2/12th_Fail_poster.jpeg"
    },
    {
        "title": "Dunki",
        "year": 2023,
        "genre": "Comedy, Drama",
        "director": "Rajkumar Hirani",
        "actors": "Shah Rukh Khan, Taapsee Pannu, Vicky Kaushal, Boman Irani, Vikram Kochhar",
        "overview": "Four friends from a small village in Punjab share a common dream of traveling to England, using an unconventional and perilous backdoor route known as Donkey Flight.",
        "imdb_rating": 6.6,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/d/df/Dunki_poster.jpg"
    },
    {
        "title": "Sam Bahadur",
        "year": 2023,
        "genre": "Biography, Drama, War",
        "director": "Meghna Gulzar",
        "actors": "Vicky Kaushal, Sanya Malhotra, Fatima Sana Shaikh, Mohammed Zeeshan Ayyub",
        "overview": "The biographical journey of Field Marshal Sam Manekshaw, India's first Field Marshal and war hero during the 1971 Indo-Pakistani War.",
        "imdb_rating": 7.8,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/4/4b/Sam_Bahadur_poster.jpg"
    },
    {
        "title": "Stree 2",
        "year": 2024,
        "genre": "Comedy, Horror",
        "director": "Amar Kaushik",
        "actors": "Shraddha Kapoor, Rajkummar Rao, Pankaj Tripathi, Abhishek Banerjee, Aparshakti Khurana",
        "overview": "The town of Chanderi is haunted once again, this time by a terrifying headless entity named Sarkata who abducts modern independent women. The gang re-unites with the mysterious Stree to defeat evil.",
        "imdb_rating": 7.1,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/c/cb/Stree_2_poster.jpg"
    },
    {
        "title": "Fighter",
        "year": 2024,
        "genre": "Action, Thriller, War",
        "director": "Siddharth Anand",
        "actors": "Hrithik Roshan, Deepika Padukone, Anil Kapoor, Karan Singh Grover, Akshay Oberoi",
        "overview": "Top Indian Air Force aviators come together to form the elite Air Dragons unit responding to militant threats in Jammu & Kashmir.",
        "imdb_rating": 6.3,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/d/df/Fighter_film_teaser.jpg"
    },
    {
        "title": "Shaitaan",
        "year": 2024,
        "genre": "Horror, Mystery, Thriller",
        "director": "Vikas Bahl",
        "actors": "Ajay Devgn, R. Madhavan, Jyotika, Janki Bodiwala, Anngad Raaj",
        "overview": "A family's tranquil farmhouse vacation turns into a terrifying hostage nightmare when a mysterious sinister stranger hypnotizes their teenage daughter with dark black magic.",
        "imdb_rating": 6.6,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/9/94/Shaitaan_2024_film_poster.jpg"
    },
    {
        "title": "Brahmāstra: Part One – Shiva",
        "year": 2022,
        "genre": "Action, Adventure, Fantasy",
        "director": "Ayan Mukerji",
        "actors": "Ranbir Kapoor, Alia Bhatt, Amitabh Bachchan, Mouni Roy, Nagarjuna Akkineni, Shah Rukh Khan",
        "overview": "A young DJ discovers his supernatural connection to fire and embarks on a mystic quest in pursuit of the Brahmastra, the lord of all ancient Astra weapons.",
        "imdb_rating": 5.6,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/4/4f/Brahmastra_Part_One_Shiva.jpg"
    },
    {
        "title": "Rocky Aur Rani Kii Prem Kahaani",
        "year": 2023,
        "genre": "Comedy, Family, Romance",
        "director": "Karan Johar",
        "actors": "Ranveer Singh, Alia Bhatt, Dharmendra, Jaya Bachchan, Shabana Azmi",
        "overview": "Flamboyant Punjabi gym-enthusiast Rocky and sharp Bengali intellectual journalist Rani fall in love despite opposing family cultures, deciding to live with each other's families before marrying.",
        "imdb_rating": 6.8,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/6/65/Rocky_Aur_Rani_Kii_Prem_Kahaani_poster.jpg"
    },
    {
        "title": "Shershaah",
        "year": 2021,
        "genre": "Action, Biography, Drama, War",
        "director": "Vishnuvardhan",
        "actors": "Sidharth Malhotra, Kiara Advani, Shiv Panditt, Nikitin Dheer",
        "overview": "The life of Param Vir Chakra-awardee Captain Vikram Batra from his youth to his valorous sacrifice during the 1999 Kargil War recapturing Point 4875.",
        "imdb_rating": 8.4,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/9/91/Shershaah_film_poster.jpg"
    },
    {
        "title": "Chandu Champion",
        "year": 2024,
        "genre": "Action, Biography, Drama, Sport",
        "director": "Kabir Khan",
        "actors": "Kartik Aaryan, Vijay Raaz, Bhuvan Arora, Yashpal Sharma, Rajpal Yadav",
        "overview": "The extraordinary inspiring true life journey of Murlikant Petkar, India's first Paralympic gold medalist who overcame war wounds, paralysis, and societal doubt.",
        "imdb_rating": 8.0,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/b/b8/Chandu_Champion_poster.jpg"
    },
    {
        "title": "Drishyam 2",
        "year": 2022,
        "genre": "Crime, Drama, Mystery, Thriller",
        "director": "Abhishek Pathak",
        "actors": "Ajay Devgn, Akshaye Khanna, Tabu, Shriya Saran, Ishita Dutta",
        "overview": "Seven years after the original incident, a renewed police investigation threatens Vijay Salgaonkar and his family as a relentless IG Tarun Ahlawat reopens the case.",
        "imdb_rating": 8.2,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/2/22/Drishyam_2_2022_film_poster.jpg"
    },
    {
        "title": "Bhool Bhulaiyaa 2",
        "year": 2022,
        "genre": "Comedy, Horror",
        "director": "Anees Bazmee",
        "actors": "Kartik Aaryan, Tabu, Kiara Advani, Rajpal Yadav, Sanjay Mishra",
        "overview": "Strangers Ruhaan and Reet inadvertently unseal an abandoned haveli where the malevolent spirit of Manjulika has been trapped for decades.",
        "imdb_rating": 5.7,
        "poster_path": "https://upload.wikimedia.org/wikipedia/en/2/23/Bhool_Bhulaiyaa_2_poster.jpg"
    }
]


def clean_title(title):
    if not isinstance(title, str):
        return ""
    # Strip (film), (year), etc.
    title = re.sub(r"\s*\([^)]*film[^)]*\)", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s*\(\d{4}\)", "", title)
    # Strip extra whitespace and quotes
    title = title.strip().strip('"').strip("'")
    return title


def normalize_clean_string(s):
    if not isinstance(s, str) or pd.isna(s):
        return ""
    # Replace pipe or semicolon with comma
    s = s.replace("|", ", ").replace(";", ", ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def build_unified_dataset():
    os.makedirs(DATA_DIR, exist_ok=True)
    print("Fetching and building Bollywood Movie Database...")

    # Load TIMDB
    df_timdb = None
    try:
        print(f"Loading TIMDB (1950-2019) from {URL_TIMDB}...")
        req = urllib.request.Request(URL_TIMDB, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            df_timdb = pd.read_csv(resp)
        print(f"TIMDB loaded: {len(df_timdb)} movies.")
    except Exception as e:
        print(f"Could not fetch TIMDB dataset: {e}")

    # Load IMDB 2023-1951
    df_imdb = None
    try:
        print(f"Loading IMDB (1951-2023) from {URL_IMDB_2023}...")
        req = urllib.request.Request(URL_IMDB_2023, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            df_imdb = pd.read_csv(resp)
        print(f"IMDB 2023 loaded: {len(df_imdb)} movies.")
    except Exception as e:
        print(f"Could not fetch IMDB 2023 dataset: {e}")

    records = []

    # Process TIMDB
    if df_timdb is not None:
        for _, row in df_timdb.iterrows():
            title = clean_title(str(row.get("title_x", "")))
            if not title or len(title) < 2:
                continue

            year_raw = row.get("year_of_release", "")
            try:
                year = int(float(str(year_raw).strip()[:4]))
            except Exception:
                year = 2000

            story = str(row.get("story", ""))
            summary = str(row.get("summary", ""))
            tagline = str(row.get("tagline", ""))
            overview_parts = [p for p in [tagline, story, summary] if p and p.lower() != "nan" and len(p.strip()) > 3]
            overview = " ".join(overview_parts).strip()
            if not overview:
                overview = f"Bollywood movie {title} released in {year}."

            rating_raw = row.get("imdb_rating", "")
            try:
                rating = round(float(rating_raw), 1)
            except Exception:
                rating = 6.5

            poster = str(row.get("poster_path", ""))
            if not poster or poster.lower() == "nan" or not poster.startswith("http"):
                poster = ""

            records.append({
                "title": title,
                "year": year,
                "genre": normalize_clean_string(str(row.get("genres", "Drama"))),
                "director": normalize_clean_string(str(row.get("directors", row.get("director", "")))),
                "actors": normalize_clean_string(str(row.get("actors", ""))),
                "overview": overview,
                "imdb_rating": rating,
                "poster_path": poster
            })

    # Process IMDB 2023-1951
    if df_imdb is not None:
        for _, row in df_imdb.iterrows():
            title = clean_title(str(row.get("movie_name", "")))
            if not title or len(title) < 2:
                continue

            year_raw = row.get("year", "")
            try:
                year = int(float(str(year_raw).strip()[:4]))
            except Exception:
                year = 2010

            overview = str(row.get("overview", "")).strip()
            if not overview or overview.lower() == "nan":
                overview = f"Bollywood movie {title} released in {year}."

            director = normalize_clean_string(str(row.get("director", "")))
            actors = normalize_clean_string(str(row.get("cast", "")))
            genre = normalize_clean_string(str(row.get("genre", "Drama")))

            records.append({
                "title": title,
                "year": year,
                "genre": genre,
                "director": director,
                "actors": actors,
                "overview": overview,
                "imdb_rating": 7.0,
                "poster_path": ""
            })

    # Add Curated Modern Blockbusters
    for movie in CURATED_MODERN_MOVIES:
        records.append(movie)

    # Convert to DataFrame
    df = pd.DataFrame(records)
    print(f"Total raw merged records: {len(df)}")

    # Deduplicate by lowercase clean title
    df["title_key"] = df["title"].str.lower().str.replace(r"[^\w\s]", "", regex=True).str.strip()

    # Aggregation function to merge best metadata across duplicate entries
    def merge_group(g):
        first = g.iloc[0].to_dict()
        # Prefer the entry with non-empty poster
        posters = [p for p in g["poster_path"] if isinstance(p, str) and p.startswith("http")]
        if posters:
            first["poster_path"] = posters[0]
        # Prefer the longest overview
        overviews = sorted([str(o) for o in g["overview"] if len(str(o)) > 10], key=len, reverse=True)
        if overviews:
            first["overview"] = overviews[0]
        # Prefer the most complete actors
        actors_list = sorted([str(a) for a in g["actors"] if len(str(a)) > 3], key=len, reverse=True)
        if actors_list:
            first["actors"] = actors_list[0]
        # Prefer non-empty director
        directors = [str(d) for d in g["director"] if len(str(d)) > 2]
        if directors:
            first["director"] = directors[0]
        # Genres
        genres = sorted([str(gen) for gen in g["genre"] if len(str(gen)) > 2], key=len, reverse=True)
        if genres:
            first["genre"] = genres[0]
        # Highest valid rating
        ratings = [r for r in g["imdb_rating"] if pd.notna(r) and 1.0 <= r <= 10.0]
        if ratings:
            first["imdb_rating"] = round(float(np.mean(ratings)), 1)
        return pd.Series(first)

    print("Deduplicating and merging fields...")
    df_merged = df.groupby("title_key", as_index=False, group_keys=False).apply(merge_group)
    df_merged = df_merged.drop(columns=["title_key"], errors="ignore")

    # Clean missing / invalid fields
    df_merged["genre"] = df_merged["genre"].replace("", "Drama, Bollywood").fillna("Drama, Bollywood")
    df_merged["actors"] = df_merged["actors"].replace("", "Ensemble Cast").fillna("Ensemble Cast")
    df_merged["director"] = df_merged["director"].replace("", "Bollywood Director").fillna("Bollywood Director")
    df_merged["overview"] = df_merged["overview"].fillna("Classic Bollywood cinema feature.")
    df_merged["imdb_rating"] = df_merged["imdb_rating"].fillna(6.8).clip(1.0, 10.0)
    df_merged["year"] = df_merged["year"].fillna(2000).astype(int)

    # Sort by year descending, then title
    df_merged = df_merged.sort_values(by=["year", "title"], ascending=[False, True]).reset_index(drop=True)

    print(f"Final clean Bollywood movies count: {len(df_merged)}")
    df_merged.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"Successfully saved clean dataset to {OUTPUT_FILE}")
    return df_merged


if __name__ == "__main__":
    build_unified_dataset()
