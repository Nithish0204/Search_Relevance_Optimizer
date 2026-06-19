import re

def extract_price(query):
    match = re.search(r"(?:below|under|less than)\s*₹?\s*(\d+)k?", query, re.IGNORECASE)
    if match:
        price = int(match.group(1))
        if "k" in match.group(0).lower():
            price *= 1000
        return price
    return None

def extract_category(query):
    categories = {
        "sneakers": ["sneakers", "shoes", "kicks"],
        "earphones": ["earphones", "headphones", "airpods"],
        "smartphone": ["phone", "smartphone", "iphone"],
    }
    query_lower = query.lower()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in query_lower:
                return category
    return None


def extract_color(query):
    colors = ["red", "blue", "black", "white", "pink", "gray", "green"]
    query_lower = query.lower()
    for color in colors:
        if color in query_lower:
            return color
    return None

def extract_filters(query):
    filters = {}

    category = extract_category(query)
    if category:
        filters["category"] = category

    color = extract_color(query)
    if color:
        filters["color"] = color

    price = extract_price(query)
    if price:
        filters["price"] = {"$lt": price}

    return filters


if __name__ == "__main__":
    print(extract_filters("red sneakers under 2k"))
    print(extract_filters("white earphones below 1000"))
    print(extract_filters("just searching randomly"))