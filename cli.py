"""
Interactive and Scriptable CLI for Bollywood Movie Recommender System.

Usage:
    python cli.py "3 Idiots"
    python cli.py "DDLJ" --top 5
    python cli.py --interactive
"""

import sys
import argparse
import codecs

# Ensure Windows terminal handles UTF-8 / emojis gracefully
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.dataset import BollywoodDataset
from src.engine import BollywoodRecommender


def print_banner():
    banner = """
======================================================================
              BOLLYWOOD MOVIE RECOMMENDER SYSTEM
       Find the 5 Most Similar Hindi Movies Across All Eras
======================================================================
"""
    print(banner)


def display_movie_card(source_movie, recommendations):
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  [SEARCHED MOVIE] {source_movie['title']} ({source_movie['year']})")
    print(f"  * IMDb Rating : {source_movie['imdb_rating']}/10")
    print(f"  * Genres      : {source_movie['genre']}")
    print(f"  * Director    : {source_movie['director']}")
    print(f"  * Key Actors  : {source_movie['actors']}")
    print(f"  * Synopsis    : {source_movie['overview'][:140]}...")
    print(f"{sep}\n")

    print(f"  >>> TOP {len(recommendations)} SIMILAR BOLLYWOOD MOVIES:")
    print(sep)

    for i, rec in enumerate(recommendations, 1):
        reasons_str = " | ".join(rec.get("reasons", []))
        print(f"  [{i}] {rec['title']} ({rec['year']})  --  {rec['similarity_score']} Match")
        print(f"      * Rating   : {rec['imdb_rating']}/10")
        print(f"      * Genres   : {rec['genre']}")
        print(f"      * Director : {rec['director']}")
        print(f"      * Cast     : {rec['actors']}")
        if reasons_str:
            print(f"      * Why      : {reasons_str}")
        print(f"      * Plot     : {rec['overview'][:120]}...")
        print()
    print(sep)


def run_interactive(recommender: BollywoodRecommender):
    print_banner()
    print("Type any Bollywood movie title, acronym (e.g. 'DDLJ', 'ZNMD'), or 'exit'/'q' to quit.\n")

    while True:
        try:
            query = input("\033[1;35mBollywood Query > \033[0m").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("\nDhanyavaad! Thank you for using Bollywood Movie Recommender! 🎬")
                break

            source, recs = recommender.recommend(query, top_k=5)
            if not source:
                print(f"\n❌ Movie '{query}' not found in the database.")
                # Give fuzzy suggestions
                titles = recommender.dataset.titles
                import difflib
                suggestions = difflib.get_close_matches(query, titles, n=3, cutoff=0.3)
                if suggestions:
                    print(f"   Did you mean: {', '.join(suggestions)}?\n")
                continue

            display_movie_card(source, recs)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Alvida! 🎬")
            break


def main():
    parser = argparse.ArgumentParser(description="Bollywood Movie Recommender CLI")
    parser.add_argument("movie", nargs="?", default=None, help="Bollywood movie title to find recommendations for")
    parser.add_argument("--top", "-k", type=int, default=5, help="Number of similar movies to recommend (default: 5)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive prompt mode")

    args = parser.parse_args()

    # Load dataset and engine
    ds = BollywoodDataset()
    rec = BollywoodRecommender(ds)

    if args.interactive or args.movie is None:
        run_interactive(rec)
    else:
        source, recs = rec.recommend(args.movie, top_k=args.top)
        if not source:
            print(f"Movie '{args.movie}' not found in the Bollywood database.")
            sys.exit(1)
        print_banner()
        display_movie_card(source, recs)


if __name__ == "__main__":
    main()
