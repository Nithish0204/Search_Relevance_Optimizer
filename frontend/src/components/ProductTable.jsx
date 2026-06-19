import API_BASE_URL from "../config";
function ProductTable({ products }) {
  return (
    <table className="product-table">

      <thead>
        <tr>
          <th>Image</th>
          <th>Title</th>
          <th>Category</th>
          <th>Brand</th>
          <th>Color</th>
          <th>Gender</th>
          <th>Price</th>
          <th>Rating</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>

        {products.map((product) => (

          <tr key={product.id || product._id}>

            <td>
              <img
                src={
                  product.image_url ||
                  "https://placehold.co/300x300?text=No+Image"
                }
                alt={product.title}
                className="table-image"
              />
            </td>

            <td>{product.title}</td>

            <td>{product.category}</td>

            <td>{product.brand}</td>

            <td>{product.color}</td>

            <td>{product.gender}</td>

            <td>₹{product.price}</td>

            <td>⭐ {product.rating}</td>

            <td>
              {product.in_stock
                ? "In Stock"
                : "Out Of Stock"}
            </td>

            <td>


              <button
  className="delete-btn"
  onClick={async () => {

    const confirmDelete =
      window.confirm(
        `Delete ${product.title}?`
      );

    if (!confirmDelete) return;

    try {

      const response = await fetch(
        `${API_BASE_URL}/products/${product.id}`,
        {
          method: "DELETE",
          headers: {
            "ngrok-skip-browser-warning":
              "true"
          }
        }
      );

      const data =
        await response.json();

      alert(data.message);

      window.location.reload();

    } catch (error) {

      console.error(error);

      alert(
        "Failed to delete product"
      );

    }

  }}
>
  Delete
</button>

            </td>

          </tr>

        ))}

      </tbody>

    </table>
  );
}

export default ProductTable;