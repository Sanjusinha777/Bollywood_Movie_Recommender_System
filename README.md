# 🎬 Bollywood Movie Recommender System

A content-based movie recommendation system covering **4,980+ Bollywood Hindi movies** spanning across **74+ years of Indian Cinema (1950 – 2024)**.

Given any Bollywood movie search query (including popular acronyms like `DDLJ`, `ZNMD`, `K3G` or misspellings), the system outputs the **5 most similar Bollywood movies** based on director style, star cast, storyline/plot, genres, and cinematic era.

---

## 🌟 Key Features

1. **Massive Bollywood Cinema Database (4,980+ Movies)**:
   - **Golden Age (1950–1979)**: *Sholay*, *Mughal-e-Azam*, *Mother India*, *Guide*, *Anand*, *Deewaar*, *Don*...
   - **Superstar & 90s Romance (1980–1999)**: *DDLJ*, *Kuch Kuch Hota Hai*, *Hum Aapke Hain Koun..*, *Andaz Apna Apna*, *Satya*...
   - **Millennium Classics (2000–2009)**: *3 Idiots*, *Lagaan*, *Dil Chahta Hai*, *Swades*, *Kal Ho Naa Ho*, *Munna Bhai M.B.B.S.*, *Chak De! India*...
   - **Modern Wave (2010–2019)**: *Dangal*, *PK*, *Bajrangi Bhaijaan*, *Gangs of Wasseypur*, *Zindagi Na Milegi Dobara*, *Queen*, *Andhadhun*, *Tumbbad*...
   - **Contemporary Blockbusters (2020–2024)**: *Jawan*, *Pathaan*, *Animal*, *12th Fail*, *Dunki*, *Sam Bahadur*, *Stree 2*, *Fighter*, *Brahmāstra*...

2. **Smart Search & Acronym Resolution**:
   - Handles acronyms automatically (e.g., `DDLJ` ➔ *Dilwale Dulhania Le Jayenge*, `ZNMD` ➔ *Zindagi Na Milegi Dobara*).
   - Tolerates minor misspellings and partial titles using fuzzy matching and normalized substring matching.

3. **Content-Based Recommendation Engine**:
   - **Enriched Metadata Soup**: Weighted combination of Director (3x), Lead Actors (2x), Genres (2x), Decade/Era (1x), and Plot Synopsis (1x).
   - Entity collapsed tokens (e.g., `shah_rukh_khan`, `rajkumar_hirani`) to avoid surname collisions.
   - TF-IDF vectorization with sublinear term-frequency and n-gram modeling.
   - Ultra-fast cosine similarity computation.

4. **Explainable Recommendations**:
   - Each recommendation includes human-readable rationale (e.g., *"Directed by Rajkumar Hirani"*, *"Starring Shah Rukh Khan"*, *"Shared genres: Drama, Comedy"*).

5. **3 Easy Ways to Run**:
   - 🌐 **Streamlit Web Application** (`app.py`): Beautiful cinematic dark UI with movie posters and interactive exploration.
   - 💻 **Interactive CLI** (`cli.py`): Quick command-line query and interactive terminal mode.
   - 🚀 **FastAPI REST API** (`api.py`): Production-ready REST endpoints (`/recommend`, `/search`, `/top-rated`).

---

## 📁 Project Structure

```text
bollywood-movie-recommender/
│
├── data/
│   └── bollywood_movies.csv      # Unified 4,980+ Bollywood movies database
│
├── src/
│   ├── __init__.py
│   ├── dataset.py                # Dataset loader, title indexing, fuzzy search & acronym map
│   ├── engine.py                 # TF-IDF & Cosine Similarity recommendation engine
│   └── poster_fetcher.py         # Poster URL management and fallback image generator
│
├── tests/
│   └── test_system.py            # Automated test suite (exact, acronym, fuzzy & 5 recs checks)
│
├── app.py                        # Streamlit Web UI application
├── cli.py                        # Terminal Command-Line Interface
├── api.py                        # FastAPI backend REST API
├── build_dataset.py              # Pipeline to fetch and merge TIMDB & IMDB datasets
├── test_recommender.py           # Quick verification script
├── requirements.txt              # Python package dependencies
└── README.md                     # Documentation
```

---

## 🚀 Getting Started

### 1. Installation

Ensure you have Python 3.10+ installed:

```bash
cd bollywood-movie-recommender
pip install -r requirements.txt
```

### 2. Run the Streamlit Web Application

```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`. Enter any Bollywood movie to get instant visual recommendations with posters and plot synopses.

### 3. Run the Command-Line Interface (CLI)

Get 5 recommendations for a movie:
```bash
python cli.py "3 Idiots"
```

Use acronyms:
```bash
python cli.py "DDLJ"
```

Or enter interactive exploration mode:
```bash
python cli.py --interactive
```

### 4. Run the REST API

```bash
uvicorn api:app --reload --port 8000
```
- Interactive API Docs: `http://localhost:8000/docs`
- Example recommendation call:
  ```bash
  curl "http://localhost:8000/recommend?movie=3%20Idiots&top_k=5"
  ```

---

## 🧪 Running Tests

Run the test suite to verify search and recommendation consistency:

```bash
python -m unittest discover tests
```

---

## 🎬 Example Outputs

### Query: `3 Idiots` (2009)
* **1. Dunki (2023)** — *Directed by Rajkumar Hirani; Shared genres: Drama, Comedy*
* **2. PK (2014)** — *Directed by Rajkumar Hirani; Starring Aamir Khan, Boman Irani*
* **3. Munna Bhai M.B.B.S. (2003)** — *Directed by Rajkumar Hirani; Starring Boman Irani*
* **4. Lage Raho Munna Bhai (2006)** — *Directed by Rajkumar Hirani; Shared genres: Drama, Comedy*
* **5. Sanju (2018)** — *Directed by Rajkumar Hirani; Shared themes: Friendship, Biographical Drama*

### Query: `DDLJ` (1995)
* **1. Mohabbatein (2000)** — *Directed by Aditya Chopra; Starring Shah Rukh Khan, Anupam Kher*
* **2. Rab Ne Bana Di Jodi (2008)** — *Directed by Aditya Chopra; Starring Shah Rukh Khan*
* **3. Kuch Kuch Hota Hai (1998)** — *Starring Shah Rukh Khan, Kajol; Shared genres: Romance, Drama*
* **4. Kabhi Khushi Kabhie Gham... (2001)** — *Starring Shah Rukh Khan, Kajol*
* **5. Dil To Pagal Hai (1997)** — *Starring Shah Rukh Khan; Shared genres: Romance, Musical*
