"""
Spelling correction using SymSpell.
Loaded lazily on first call — not at import time.

Protected words (brand names, categories) are loaded DYNAMICALLY
from Elasticsearch via registry.py — no hardcoded lists.
"""

from symspellpy import SymSpell, Verbosity
from importlib.resources import files as importlib_files
from nlp.registry import get_brands, get_categories

_sym_spell = None

def _get_symspell() -> SymSpell:
    global _sym_spell
    if _sym_spell is None:
        _sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        dict_path = str(
            importlib_files("symspellpy").joinpath("frequency_dictionary_en_82_765.txt")
        )
        _sym_spell.load_dictionary(dict_path, term_index=0, count_index=1)
        
        # Boost our domain-specific words (categories, brands) so they rank higher 
        # than generic English words during correction (e.g. 'shos' -> 'shoes' instead of 'show')
        domain_words = set(get_brands()) | set(get_categories())
        # Also add singulars/plurals of categories
        extra_words = set()
        for w in domain_words:
            if w.endswith('s'):
                extra_words.add(w[:-1])
            else:
                extra_words.add(w + 's')
        
        for word in domain_words | extra_words:
            _sym_spell.create_dictionary_entry(word, 999999999) # extremely high frequency

    return _sym_spell

def correct_spelling(text: str) -> str:
    """
    Correct each word individually.
    Protected words (brands + categories from ES) are returned unchanged.

    Example:
        "snekar for men"  →  "sneaker for men"
        "airpodds"        →  "airpods"  (if "airpods" is in SymSpell dict)
        "boat"            →  "boat"     (protected — exists as brand in ES)
    """
    sym   = _get_symspell()
    words = text.split()

    # dynamically load protected words from ES
    protected = set(get_brands()) | set(get_categories())

    result = []
    for word in words:
        if word in protected or word.isdigit():
            result.append(word)
            continue
        suggestions = sym.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)
        result.append(suggestions[0].term if suggestions else word)
    return " ".join(result)
