function ProductCard({ product }) {
  return (
    <div className="product-card">

      <div className="product-image-container">
        <img
          src={
            product.image_url ||
            "https://placehold.co/300x300?text=No+Image"
          }
          alt={product.title}
        />
      </div>

      <div className="product-info">

        <h3>{product.title}</h3>

        <span className="brand-badge">
          {product.brand}
        </span>

        <p className="price">
          ₹{product.price}
        </p>

        <div className="rating-stock">

          <span className="rating">
            ⭐ {product.rating}
          </span>

          <span
            className={
              product.in_stock
                ? "stock in-stock"
                : "stock out-stock"
            }
          >
            {product.in_stock
              ? "In Stock"
              : "Out of Stock"}
          </span>

        </div>

        <button className="view-btn">
          View Product
        </button>

      </div>

    </div>
  );
}

export default ProductCard;