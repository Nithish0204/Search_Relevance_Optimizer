from database import products_collection

updates = {
    "Wireless Bluetooth Earbuds": "https://placehold.co/300x300?text=Earbuds",
    "Red Running Sneakers": "https://placehold.co/300x300?text=Sneakers",
    "Men's White Sneakers": "https://placehold.co/300x300?text=Sneakers",
    "Noise Cancelling Headphones": "https://placehold.co/300x300?text=Headphones",
    "Budget Wireless Earphones": "https://placehold.co/300x300?text=Earphones",
    "Women's Pink Sneakers": "https://placehold.co/300x300?text=Sneakers",
    "iPhone 13": "https://placehold.co/300x300?text=iPhone",
    "Refurbished OnePlus Nord": "https://placehold.co/300x300?text=OnePlus",
    "Men's Black Formal Shoes": "https://placehold.co/300x300?text=Shoes",
    "Kids Velcro Sneakers": "https://placehold.co/300x300?text=Sneakers",
}

for title, url in updates.items():
    result = products_collection.update_one(
        {"title": title},
        {"$set": {"image_url": url}}
    )
    print(f"{title}: matched {result.matched_count}, modified {result.modified_count}")