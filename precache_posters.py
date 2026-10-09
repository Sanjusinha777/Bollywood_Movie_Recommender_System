"""
Pre-caches high-definition movie posters for top Bollywood cinema hits.
"""

from src.dataset import BollywoodDataset
from src.engine import BollywoodRecommender

def precache():
    ds = BollywoodDataset()
    rec = BollywoodRecommender(ds)

    popular_picks = [
        "3 Idiots",
        "Dilwale Dulhania Le Jayenge",
        "Sholay",
        "Zindagi Na Milegi Dobara",
        "Jawan",
        "12th Fail",
        "Gangs of Wasseypur",
        "Dangal",
        "PK",
        "Munna Bhai M.B.B.S.",
        "Lage Raho Munna Bhai",
        "Queen",
        "Andhadhun",
        "Jab We Met",
        "Swades",
        "Chak De! India",
        "Dunki",
        "Pathaan",
        "Animal",
        "Stree 2",
        "Fighter"
    ]

    print("Pre-caching high-definition movie posters...")
    for title in popular_picks:
        src, recs = rec.recommend(title, top_k=5)
        if src:
            print(f"[OK] Cached {src['title']} and {len(recs)} similar movies")

    print("\nAll landmark movie posters are cached in high resolution!")

if __name__ == "__main__":
    precache()
