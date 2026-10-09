"""
Enhanced Poster Fetcher and High-Resolution Cinema Card Generator.
Ensures crystal-clear posters for all Bollywood movies by:
1. Cleaning and resolving full-resolution Wikimedia URLs (removing deprecated /thumb/220px- limits).
2. Querying Wikipedia's official REST API for high-res movie posters.
3. Local disk caching for instant zero-lag rendering without hotlinking or CORS blocks.
4. High-Definition (400x600) stylized cinematic poster generation with TrueType typography for films without online images.
"""

import os
import re
import urllib.parse
import urllib.request
import json
import hashlib
from PIL import Image, ImageDraw, ImageFont

CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "posters_cache"
)
os.makedirs(CACHE_DIR, exist_ok=True)

USER_AGENT = "BollywoodRecommender/2.0 (HindiCinemaProject; contact: contact@bollywoodrecommender.local)"

# Color themes based on primary genre
GENRE_PALETTES = {
    "action": {"bg_top": (45, 10, 10), "bg_bot": (15, 5, 5), "accent": (239, 68, 68)},
    "romance": {"bg_top": (55, 15, 35), "bg_bot": (20, 5, 15), "accent": (244, 114, 182)},
    "comedy": {"bg_top": (45, 35, 10), "bg_bot": (20, 15, 5), "accent": (251, 191, 36)},
    "thriller": {"bg_top": (15, 20, 30), "bg_bot": (8, 10, 18), "accent": (14, 165, 233)},
    "crime": {"bg_top": (25, 25, 28), "bg_bot": (10, 10, 12), "accent": (245, 158, 11)},
    "horror": {"bg_top": (20, 10, 25), "bg_bot": (8, 4, 10), "accent": (168, 85, 247)},
    "drama": {"bg_top": (20, 25, 45), "bg_bot": (10, 12, 25), "accent": (96, 165, 250)},
    "biography": {"bg_top": (35, 30, 20), "bg_bot": (15, 12, 8), "accent": (217, 119, 6)},
}
DEFAULT_PALETTE = {"bg_top": (22, 27, 34), "bg_bot": (10, 12, 16), "accent": (245, 166, 35)}


def clean_wikimedia_url(url: str) -> str:
    """Converts low-res or deprecated /thumb/.../220px-... Wikimedia URL to full-res original URL."""
    if not url or not isinstance(url, str):
        return ""
    # Example: https://upload.wikimedia.org/wikipedia/en/thumb/d/df/3_idiots_poster.jpg/220px-3_idiots_poster.jpg
    # Target: https://upload.wikimedia.org/wikipedia/en/d/df/3_idiots_poster.jpg
    m = re.match(r"^(https://upload\.wikimedia\.org/wikipedia/[^/]+)/thumb/(.+)/[^/]+$", url)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return url


def download_image(url: str, dest_path: str) -> bool:
    """Safely downloads an image and writes to dest_path if valid."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=4) as response:
            content_type = response.headers.get("Content-Type", "")
            data = response.read()
            if len(data) > 1500 and ("image" in content_type or url.endswith((".jpg", ".jpeg", ".png", ".webp"))):
                with open(dest_path, "wb") as f:
                    f.write(data)
                return True
    except Exception:
        pass
    return False


def fetch_from_wikipedia_api(title: str, year: int, dest_path: str) -> bool:
    """Queries Wikipedia official REST API to find the high-res movie poster."""
    candidates = [
        f"{title} (film)",
        title,
        f"{title} ({year} film)",
        f"{title} (Hindi film)"
    ]

    for cand in candidates:
        formatted_title = urllib.parse.quote(cand.replace(" ", "_"))
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_title}"
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                # Prefer full originalimage, fallback to thumbnail
                img_url = (data.get("originalimage") or {}).get("source") or (data.get("thumbnail") or {}).get("source")
                if img_url:
                    clean_url = clean_wikimedia_url(img_url)
                    if download_image(clean_url, dest_path):
                        return True
        except Exception:
            continue
    return False


def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Loads a crisp system TrueType font with graceful fallback."""
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "arial.ttf"
    ]
    for p in font_paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def generate_hd_cinema_poster(title: str, year: int, genre: str, rating: float, dest_path: str):
    """
    Generates a crystal-clear 400x600 HD Cinema Poster Card
    with custom gradients, golden borders, clean typography, and badges.
    """
    width, height = 400, 600
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Determine genre palette
    primary_genre = genre.split(",")[0].strip().lower() if genre else "drama"
    palette = GENRE_PALETTES.get(primary_genre, DEFAULT_PALETTE)
    top_color = palette["bg_top"]
    bot_color = palette["bg_bot"]
    accent = palette["accent"]

    # Draw vertical background gradient
    for y in range(height):
        factor = y / height
        r = int(top_color[0] * (1 - factor) + bot_color[0] * factor)
        g = int(top_color[1] * (1 - factor) + bot_color[1] * factor)
        b = int(top_color[2] * (1 - factor) + bot_color[2] * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Outer and inner decorative cinema borders
    draw.rectangle([12, 12, width - 13, height - 13], outline=(245, 166, 35, 180), width=2)
    draw.rectangle([18, 18, width - 19, height - 19], outline=(60, 65, 80), width=1)

    # Top Cinema Tag
    font_tag = get_font(13, bold=True)
    draw.text((width // 2, 45), "[ BOLLYWOOD CINEMA ]", fill=(245, 166, 35), font=font_tag, anchor="mm")

    # Center Film Reel Icon / Glyphs
    draw.ellipse([width // 2 - 40, 100, width // 2 + 40, 180], outline=accent, width=3)
    draw.ellipse([width // 2 - 25, 115, width // 2 + 25, 165], outline=(245, 166, 35), width=2)
    draw.line([(width // 2 - 35, 140), (width // 2 + 35, 140)], fill=accent, width=2)
    draw.line([(width // 2, 105), (width // 2, 175)], fill=accent, width=2)

    # Wrap title into lines
    font_title = get_font(24, bold=True)
    words = title.split()
    lines = []
    current_line = []
    for w in words:
        current_line.append(w)
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font_title)
        if (bbox[2] - bbox[0]) > 320:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [w]
    if current_line:
        lines.append(" ".join(current_line))

    # If title is too long, shrink font
    if len(lines) > 3:
        font_title = get_font(19, bold=True)

    # Render Title
    title_start_y = 230
    line_height = 32
    for i, line in enumerate(lines[:4]):
        draw.text((width // 2, title_start_y + (i * line_height)), line, fill=(255, 255, 255), font=font_title, anchor="mm")

    # Release Year Badge Pill
    year_y = title_start_y + (len(lines) * line_height) + 25
    pill_w = 80
    draw.rounded_rectangle([width // 2 - pill_w // 2, year_y - 14, width // 2 + pill_w // 2, year_y + 14], radius=14, fill=(35, 42, 55))
    font_year = get_font(14, bold=True)
    draw.text((width // 2, year_y), str(year), fill=(229, 231, 235), font=font_year, anchor="mm")

    # Genre Text
    font_genre = get_font(13, bold=False)
    clean_genre = ", ".join([g.strip().upper() for g in genre.split(",")[:2]])
    draw.text((width // 2, year_y + 40), clean_genre, fill=accent, font=font_genre, anchor="mm")

    # Star Rating Box at bottom
    rating_y = height - 70
    draw.rounded_rectangle([width // 2 - 80, rating_y - 18, width // 2 + 80, rating_y + 18], radius=8, fill=(245, 166, 35))
    font_rating = get_font(15, bold=True)
    rating_str = f"IMDb: {rating:.1f} / 10"
    draw.text((width // 2, rating_y), rating_str, fill=(15, 20, 25), font=font_rating, anchor="mm")

    # Save HD image
    img.save(dest_path, "JPEG", quality=95)


def get_poster_url(
    poster_path: str,
    title: str,
    genre: str = "",
    year: int = 2000,
    imdb_rating: float = 7.0
) -> str:
    """
    Main entry point: returns a crystal-clear, verified poster path.
    1. Checks local cache for prior high-res download or generated poster.
    2. Downloads and caches full-res Wikimedia original image.
    3. Searches Wikipedia REST API if needed.
    4. Falls back to generating a gorgeous HD cinema card.
    Always returns an absolute local file path for reliable, instant rendering.
    """
    safe_key = hashlib.md5(f"{title}_{year}".lower().encode("utf-8")).hexdigest()
    cache_file = os.path.join(CACHE_DIR, f"{safe_key}.jpg")

    # 1. Cache hit
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 1200:
        return cache_file

    # 2. Try raw poster_path from database
    if poster_path and isinstance(poster_path, str) and poster_path.startswith("http"):
        clean_url = clean_wikimedia_url(poster_path)
        if download_image(clean_url, cache_file):
            return cache_file

    # 3. Query Wikipedia official REST API
    if fetch_from_wikipedia_api(title, year, cache_file):
        return cache_file

    # 4. Generate HD Cinema Card
    generate_hd_cinema_poster(title, year, genre, imdb_rating, cache_file)
    return cache_file
