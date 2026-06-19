from database import products_collection

products = [
    {"title": "Wireless Bluetooth Earbuds", "category": "earphones", "color": "black", "price": 1499, "gender": "unisex", "rating": 4.2, "brand": "boAt", "in_stock": True, "image_url": "https://placehold.co/300x300?text=Earbuds"},
    {"title": "Red Running Sneakers", "category": "sneakers", "color": "red", "price": 1299, "gender": "women", "rating": 4.0, "brand": "Sparx", "in_stock": True, "image_url": "https://placehold.co/300x300?text=Sneakers"},
    {"title": "Men's White Sneakers", "category": "sneakers", "color": "white", "price": 1899, "gender": "men", "rating": 4.5, "brand": "Nike", "in_stock": True, "image_url": "https://placehold.co/300x300?text=Sneakers"},
    {"title": "Noise Cancelling Headphones", "category": "headphones", "color": "black", "price": 2499, "gender": "unisex", "rating": 4.3, "brand": "Sony", "in_stock": True, "image_url": "https://placehold.co/300x300?text=Headphones"},
    {"title": "Budget Wireless Earphones", "category": "earphones", "color": "white", "price": 999, "gender": "unisex", "rating": 3.8, "brand": "Mivi", "in_stock": True, "image_url": "https://placehold.co/300x300?text=Earphones"},
    {"title": "Women's Pink Sneakers", "category": "sneakers", "color": "pink", "price": 1450, "gender": "women", "rating": 4.1, "brand": "Adidas", "in_stock": False, "image_url": "https://placehold.co/300x300?text=Sneakers"},
    {"title": "iPhone 13", "category": "smartphone", "color": "blue", "price": 54999, "gender": "unisex", "rating": 4.7, "brand": "Apple", "in_stock": True, "image_url": "https://placehold.co/300x300?text=iPhone"},
    {"title": "Refurbished OnePlus Nord", "category": "smartphone", "color": "gray", "price": 14999, "gender": "unisex", "rating": 4.0, "brand": "OnePlus", "in_stock": True, "image_url": "https://placehold.co/300x300?text=OnePlus"},
    {"title": "Men's Black Formal Shoes", "category": "shoes", "color": "black", "price": 1799, "gender": "men", "rating": 4.2, "brand": "Bata", "in_stock": True, "image_url": "https://placehold.co/300x300?text=Shoes"},
    {"title": "Kids Velcro Sneakers", "category": "sneakers", "color": "blue", "price": 899, "gender": "kids", "rating": 3.9, "brand": "Campus", "in_stock": True, "image_url": "https://placehold.co/300x300?text=Sneakers"},
]

result = products_collection.insert_many(products)
print(f"Inserted {len(result.inserted_ids)} products successfully.")