"""
Entity extraction from normalized query text.
Extracts: price range, brand, color, gender, category, keywords.
Uses spaCy for NLP + RapidFuzz for brand fuzzy matching.

All reference data (brands, colors, categories) is loaded DYNAMICALLY
from Elasticsearch via registry.py — no hardcoded lists.

IMPORTANT: No synonym expansion here.
           Synonyms are handled by the Elasticsearch analyzer.
"""

import re
import spacy
from rapidfuzz import process
from typing import Optional, List, Tuple
from nlp.registry import get_brands, get_colors, get_categories

# load spaCy model once at module level
_nlp = spacy.load("en_core_web_sm")

# ── extractors ────────────────────────────────────────────────────

def extract_price(text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract price_min and price_max from text.

    Handles:
        "under 2000"              → (None, 2000)
        "below 1500"              → (None, 1500)
        "less than 3000"          → (None, 3000)
        "above 500"               → (500, None)
        "more than 1000"          → (1000, None)
        "between 500 and 2000"    → (500, 2000)
        "500 to 2000"             → (500, 2000)
        "around 1500"             → (1200, 1800)  ← ±20%
    """
    price_min = None
    price_max = None

    # range: "500 to 2000" or "between 500 and 2000" or "500-2000"
    range_match = re.search(
        r'(?:between\s+)?(\d+)\s*(?:to|-|and)\s*(\d+)', text
    )
    if range_match:
        price_min = float(range_match.group(1))
        price_max = float(range_match.group(2))
        return price_min, price_max

    # max price: "under", "below", "less than", "within", "upto"
    max_match = re.search(
        r'(?:under|below|less\s+than|within|upto|up\s+to|max|maximum)\s+(\d+)',
        text
    )
    if max_match:
        price_max = float(max_match.group(1))

    # min price: "above", "more than", "over", "minimum", "atleast"
    min_match = re.search(
        r'(?:above|more\s+than|over|minimum|atleast|at\s+least)\s+(\d+)',
        text
    )
    if min_match:
        price_min = float(min_match.group(1))

    # approximate: "around 1500", "approximately 2000"
    approx_match = re.search(
        r'(?:around|approximately|roughly|about)\s+(\d+)', text
    )
    if approx_match and not price_min and not price_max:
        val = float(approx_match.group(1))
        price_min = val * 0.8
        price_max = val * 1.2

    return price_min, price_max

def extract_brand(text: str) -> Optional[str]:
    """
    Fuzzy match against dynamically loaded brands from ES using RapidFuzz.
    Returns brand in lowercase if match score >= 80, else None.

    Falls back to spaCy NER (ORG entities) if no ES brands are available.

    Example:
        "nkie shoes"     →  "nike"     (fuzzy match from ES brands)
        "boat earphones" →  "boat"     (exact match from ES brands)
    """
    brands = get_brands()
    colors = get_colors()
    words  = text.split()

    # strategy 1: fuzzy match against ES brands (if available)
    if brands:
        for word in words:
            if len(word) < 2 or word in colors:
                continue
            result = process.extractOne(word, brands)
            if result:
                match, score, _ = result
                if score >= 80:
                    return match.lower()

    # strategy 2: spaCy NER fallback — detect ORG/PRODUCT entities
    if not brands:
        doc = _nlp(text)
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT"):
                return ent.text.lower()

    return None

def extract_color(text: str) -> Optional[str]:
    """
    Match text words against dynamically loaded colors from ES.
    Returns first color found, or None.

    Falls back to spaCy ADJ (adjective) tagging if no ES colors are available.
    """
    colors = get_colors()
    words  = text.split()

    # match against ES colors
    if colors:
        for word in words:
            if word in colors:
                return word

    # fallback: check spaCy for known color-like adjectives
    if not colors:
        doc = _nlp(text)
        # basic fallback — common colors that are universally known
        _BASIC_COLORS = {
            "red", "blue", "black", "white", "green", "yellow", "pink",
            "grey", "gray", "silver", "gold", "orange", "purple", "brown"
        }
        for token in doc:
            if token.text.lower() in _BASIC_COLORS:
                return token.text.lower()

    return None

def extract_gender(text: str) -> Optional[str]:
    """
    Detect gender from common patterns.
    Returns "men", "women", or "unisex", or None.

    This stays regex-based because gender terms are universal —
    they don't depend on what products are in the database.

    Examples:
        "for men"     → "men"
        "for women"   → "women"
        "men's"       → "men"
        "ladies bag"  → "women"  (already normalized in normalizer.py)
        "unisex"      → "unisex"
    """
    if re.search(r"\bunisex\b", text):
        return "unisex"
    if re.search(r"\b(for\s+)?women('s)?\b", text):
        return "women"
    if re.search(r"\b(for\s+)?men('s)?\b", text):
        return "men"
    return None

def extract_category(text: str) -> Optional[str]:
    """
    Match tokens against dynamically loaded categories from ES.
    Uses spaCy lemmatization for better matching.
    Returns matched category string, or None.

    Example:
        "wireless headphones" → "headphones"  (if "headphones" exists in ES)
        "running shoes"       → "shoes"       (via spaCy lemma: shoe → shoes)
    """
    categories = get_categories()
    if not categories:
        return None

    # build a quick lookup set for O(1) matching
    cat_set = set(categories)

    doc = _nlp(text)

    # check lemmatized tokens first (shoe → shoes, headphone → headphones)
    for token in doc:
        lemma = token.lemma_.lower()
        if lemma in cat_set:
            return lemma
        # also check plural/singular forms
        if lemma + "s" in cat_set:
            return lemma + "s"
        if lemma.endswith("s") and lemma[:-1] in cat_set:
            return lemma[:-1]

    # check raw tokens
    for word in text.split():
        if word in cat_set:
            return word

    return None

def extract_keywords(text: str) -> List[str]:
    """
    Extract meaningful keywords after removing stop words,
    punctuation, single chars, and pure numbers.

    Uses dynamically loaded reference data to filter out
    already-extracted entities (colors, gender terms).

    Returns: lowercase list, deduplicated, max 6 keywords.
    """
    doc    = _nlp(text)
    colors = set(get_colors())

    # filter words — gender/price terms are universal, not product-dependent
    stop = colors | {
        "men", "women", "unisex", "for", "under",
        "above", "below", "between", "around",
        "less", "than", "more", "buy", "get",
        "want", "need", "good", "best",
    }

    seen   = set()
    result = []

    for token in doc:
        word = token.text.lower()
        if (
            token.is_stop        or
            token.is_punct       or
            token.is_space       or
            token.is_digit       or
            len(word) <= 1       or
            word in stop         or
            word in seen
        ):
            continue
        seen.add(word)
        result.append(word)
        if len(result) >= 6:
            break

    return result
