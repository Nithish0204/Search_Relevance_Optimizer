function ProductCard({ product }) {
  return (
    <div className="product-card">

      <img
        src={product.image}
        alt={product.name}
      />

      <h3>{product.name}</h3>

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
        {product.stock ? "In Stock" : "Out of Stock"}
      </p>

      <button>
        View Product
      </button>

    </div>
  );
}

export default ProductCard;