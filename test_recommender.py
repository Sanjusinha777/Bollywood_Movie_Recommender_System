from src.dataset import BollywoodDataset
from src.engine import BollywoodRecommender

def main():
    ds = BollywoodDataset()
    rec = BollywoodRecommender(ds)

    test_queries = [
        "3 Idiots",
        "ddlj",
        "Sholay",
        "Gangs of Wasseypur",
        "Jawan",
        "Zindagi Na Milegi Dobara",
        "12th Fail"
    ]

    for q in test_queries:
        src, recs = rec.recommend(q, top_k=5)
        print("=" * 60)
        if src:
            print(f"QUERY: '{q}' -> MATCHED: '{src['title']}' ({src['year']})")
            print(f"GENRES: {src['genre']} | DIRECTOR: {src['director']} | RATING: {src['imdb_rating']}")
            print("TOP 5 SIMILAR BOLLYWOOD MOVIES:")
            for i, r in enumerate(recs, 1):
                reasons_str = "; ".join(r["reasons"])
                print(f"  {i}. {r['title']} ({r['year']}) [{r['similarity_score']}] - {r['genre']}")
                print(f"     Reasons: {reasons_str}")
        else:
            print(f"FAILED TO MATCH: '{q}'")

if __name__ == "__main__":
    main()
