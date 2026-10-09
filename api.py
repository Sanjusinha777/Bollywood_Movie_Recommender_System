"""
FastAPI REST API for Bollywood Movie Recommender System.

Run with:
    uvicorn api:app --reload --port 8000
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
import difflib

from src.dataset import BollywoodDataset
from src.engine import BollywoodRecommender

app = FastAPI(
    title="Bollywood Movie Recommender API",
    description="High performance content-based recommender API for 4,900+ Bollywood Hindi movies.",
    version="1.0.0"
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize dataset and recommender
dataset = BollywoodDataset()
recommender = BollywoodRecommender(dataset)


@app.get("/")
def home():
    return {
        "service": "Bollywood Movie Recommender API",
        "movies_count": len(dataset.df),
        "status": "healthy",
        "docs_url": "/docs",
        "endpoints": {
            "recommend": "/recommend?movie={title}&top_k=5",
            "search": "/search?q={query}",
            "top_rated": "/top-rated?limit=10",
            "eras": "/eras"
        }
    }


@app.get("/recommend")
def recommend_movie(
    movie: str = Query(..., description="Movie title or acronym to find similar films for"),
    top_k: int = Query(5, ge=1, le=20, description="Number of recommendations to return (default: 5)")
):
    source, recs = recommender.recommend(movie, top_k=top_k)
    if not source:
        # Provide suggestions
        suggestions = difflib.get_close_matches(movie, dataset.titles, n=3, cutoff=0.3)
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Movie '{movie}' not found in Bollywood database.",
                "suggestions": suggestions
            }
        )

    return {
        "searched_movie": source,
        "recommendations_count": len(recs),
        "recommendations": recs
    }


@app.get("/search")
def search_titles(
    q: str = Query(..., min_length=1, description="Search term for title auto-complete"),
    limit: int = Query(10, ge=1, le=50)
):
    clean_q = q.lower().strip()
    # Direct substring matches first
    exact_matches = [t for t in dataset.titles if clean_q in t.lower()]
    if len(exact_matches) < limit:
        fuzzy = difflib.get_close_matches(clean_q, [t for t in dataset.titles if t not in exact_matches], n=limit - len(exact_matches), cutoff=0.4)
        exact_matches.extend(fuzzy)

    return {
        "query": q,
        "results": exact_matches[:limit]
    }


@app.get("/top-rated")
def top_rated(limit: int = Query(10, ge=1, le=50)):
    return {
        "count": limit,
        "movies": dataset.get_top_rated(limit=limit)
    }


@app.get("/health")
def health():
    return {"status": "ok", "loaded_movies": len(dataset.df)}
