import { useEffect, useState } from "react";
import ProductTable from "../components/ProductTable";
import API_BASE_URL from "../config";

function ManageProducts() {

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

useEffect(() => {

  fetch(`${API_BASE_URL}/products`, {
    headers: {
      "ngrok-skip-browser-warning": "true"
    }
  })
    .then((response) => response.json())
    .then((data) => {

      console.log(data);

      setProducts(data.products || []);
      setLoading(false);

    })
    .catch((error) => {

      console.error("Fetch Error:", error);
      setLoading(false);

    });

}, []);

  return (
    <div className="admin-page">

      <h1 className="results-title">
        Manage Products
      </h1>

      {loading ? (
        <h2>Loading Products...</h2>
      ) : (
        <ProductTable products={products} />
      )}

    </div>
  );
}

export default ManageProducts;