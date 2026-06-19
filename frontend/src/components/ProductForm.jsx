import { useState } from "react";
import API_BASE_URL from "../config";

function ProductForm() {
  const [product, setProduct] = useState({
    title: "",
    category: "",
    color: "",
    price: "",
    gender: "",
    rating: "",
    brand: "",
    in_stock: true,
    image_url: ""
  });

  const handleChange = (e) => {
    const { name, value } = e.target;

    setProduct({
      ...product,
      [name]:
        name === "in_stock"
          ? value === "true"
          : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {

      const response = await fetch(
        `${API_BASE_URL}/products`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true"
          },
          body: JSON.stringify({
            ...product,
            price: Number(product.price),
            rating: Number(product.rating)
          })
        }
      );

      const data = await response.json();

      alert(data.message);

      setProduct({
        title: "",
        category: "",
        color: "",
        price: "",
        gender: "",
        rating: "",
        brand: "",
        in_stock: true,
        image_url: ""
      });

    } catch (error) {

      console.error(error);
      alert("Failed to add product");

    }
  };

  return (
    <form
      className="product-form"
      onSubmit={handleSubmit}
    >
      <h2>Add Product</h2>

      <input
        type="text"
        name="title"
        placeholder="Product Title"
        value={product.title}
        onChange={handleChange}
        required
      />

      <input
        type="text"
        name="category"
        placeholder="Category"
        value={product.category}
        onChange={handleChange}
        required
      />

      <input
        type="text"
        name="color"
        placeholder="Color"
        value={product.color}
        onChange={handleChange}
        required
      />

      <input
        type="number"
        name="price"
        placeholder="Price"
        value={product.price}
        onChange={handleChange}
        required
      />

      <input
        type="text"
        name="gender"
        placeholder="Gender"
        value={product.gender}
        onChange={handleChange}
        required
      />

      <input
        type="number"
        step="0.1"
        name="rating"
        placeholder="Rating"
        value={product.rating}
        onChange={handleChange}
        required
      />

      <input
        type="text"
        name="brand"
        placeholder="Brand"
        value={product.brand}
        onChange={handleChange}
        required
      />

      <input
        type="text"
        name="image_url"
        placeholder="Image URL"
        value={product.image_url}
        onChange={handleChange}
        required
      />

      <select
        name="in_stock"
        value={product.in_stock.toString()}
        onChange={handleChange}
      >
        <option value="true">
          In Stock
        </option>

        <option value="false">
          Out Of Stock
        </option>
      </select>

      <button type="submit">
        Add Product
      </button>

    </form>
  );
}

export default ProductForm;