from pydantic import BaseModel
from typing import Optional, List

class ParsedQuery(BaseModel):
    """
    Structured output of the NLP parser.
    Always returned by parse_query() — never a plain dict.
    """
    keywords:         List[str]      = []
    price_min:        Optional[float] = None
    price_max:        Optional[float] = None
    brand:            Optional[str]   = None
    color:            Optional[str]   = None
    gender:           Optional[str]   = None
    category:         Optional[str]   = None
    rating_min:       Optional[float] = None
    corrected_query:  Optional[str]   = None

    class Config:
        # allow the backend to use this model directly
        from_attributes = True
