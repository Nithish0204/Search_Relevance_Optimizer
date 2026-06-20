function ProductCard({ product }) {
  return (
    <div className="product-card">

      <img
        src={
          product.image_url ||
          "https://placehold.co/300x300?text=No+Image"
        }
        alt={product.title}
      />

      <h3>{product.title}</h3>

      <p className="price">
        ₹{product.price}
      </p>

      <p>
        ⭐ {product.rating}
      </p>

      <p>
        Brand: {product.brand}
      </p>

      <p>
        Category: {product.category}
      </p>

      <p>
        {
          product.in_stock
            ? "In Stock"
            : "Out of Stock"
        }
      </p>

      <button>
        View Product
      </button>

    </div>
  );
}

export default ProductCard;