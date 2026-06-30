"""
Main NLP query parser.
Entry point: parse_query(raw: str) → ParsedQuery

Pipeline (in order):
    1. Preprocess  — lowercase, remove punctuation
    2. Spell fix   — SymSpell word-by-word correction
    3. Normalize   — "2k"→"2000", "mens"→"men"
    4. Extract     — price, brand, color, gender, category, keywords
    5. Return      — ParsedQuery Pydantic model
"""

import re
from nlp.models     import ParsedQuery
from nlp.spell      import correct_spelling
from nlp.normalizer import normalize
from nlp.entities   import (
    extract_price,
    extract_brand,
    extract_color,
    extract_gender,
    extract_category,
    extract_keywords,
)

def parse_query(raw: str) -> ParsedQuery:
    """
    Convert raw user query into a structured ParsedQuery.

    Example:
        Input  → "Airpodds under 2k for womens by boAt"
        Output → ParsedQuery(
                     keywords=["airpods"],
                     price_max=2000.0,
                     brand="boat",
                     gender="women",
                     corrected_query="airpods under 2000 for women by boat"
                 )
    """

    # ── Stage 1: Preprocess ──────────────────────────────────────
    text = raw.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)   # remove punctuation
    text = re.sub(r'\s+',     ' ', text).strip()

    # ── Stage 2: Normalize ───────────────────────────────────────
    normalized = normalize(text)

    # ── Stage 3: Spell correction ────────────────────────────────
    corrected = correct_spelling(normalized)

    # ── Stage 4: Entity extraction ───────────────────────────────
    price_min, price_max = extract_price(corrected)
    brand                = extract_brand(corrected)
    color                = extract_color(corrected)
    gender               = extract_gender(corrected)
    category             = extract_category(corrected)
    keywords             = extract_keywords(corrected)

    # ── Stage 5: Return ParsedQuery ──────────────────────────────
    corrected_query = corrected if corrected != text else None

    return ParsedQuery(
        keywords        = keywords,
        price_min       = price_min,
        price_max       = price_max,
        brand           = brand,
        color           = color,
        gender          = gender,
        category        = category,
        corrected_query = corrected_query,
    )
