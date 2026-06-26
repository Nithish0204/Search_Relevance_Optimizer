"""
Text normalization rules.
Runs AFTER spell correction, BEFORE entity extraction.
Converts shorthand and informal text into standard forms.
"""

import re

def normalize(text: str) -> str:
    """
    Normalize common shorthand expressions.

    Examples:
        "2k"     → "2000"
        "mens"   → "men"
        "womens" → "women"
        "phn"    → "phone"
        "lappy"  → "laptop"
    """

    # numeric shorthand: "2k" → "2000", "15k" → "15000"
    text = re.sub(
        r'(\d+)\s*k\b',
        lambda m: str(int(m.group(1)) * 1000),
        text,
        flags=re.IGNORECASE
    )

    # gender normalizations
    replacements = [
        ("mens",    "men"),
        ("womens",  "women"),
        ("ladies",  "women"),
        ("gents",   "men"),
        ("female",  "women"),
        ("male",    "men"),

        # device shorthand
        ("phn",    "phone"),
        ("mob",    "mobile"),
        ("lappy",  "laptop"),
        ("tab",    "tablet"),
        ("tws",    "earbuds"),
        ("iphon",  "iphone"),
        
        # typos not caught by spell checker
        ("snekar", "sneaker"),
        ("snekers", "sneakers"),

        # price words
        ("rs",     ""),
        ("inr",    ""),
        ("rupees", ""),
    ]
    for old, new in replacements:
        text = re.sub(rf'\b{old}\b', new, text, flags=re.IGNORECASE)

    # collapse extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text
