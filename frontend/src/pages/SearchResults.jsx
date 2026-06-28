import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";

import Navbar from "../components/Navbar";
import Filters from "../components/Filters";
import ProductCard from "../components/ProductCard";

import API_BASE_URL from "../config";

function SearchResults() {

  const [searchParams] = useSearchParams();

  const query =
    searchParams.get("q") || "";

  const [products, setProducts] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [selectedBrand,
    setSelectedBrand] =
    useState("");

  const [selectedRating,
    setSelectedRating] =
    useState(0);

  useEffect(() => {

    setLoading(true);

    let url = query === ""
      ? `${API_BASE_URL}/products?`
      : `${API_BASE_URL}/search?q=${encodeURIComponent(query)}&`;

    if (selectedBrand) {
      url += `brand=${encodeURIComponent(selectedBrand)}&`;
    }
    if (selectedRating > 0) {
      url += `rating=${selectedRating}&`;
    }

    fetch(url, {
      headers: {
        "ngrok-skip-browser-warning":
          "true"
      }
    })
      .then((response) =>
        response.json()
      )
      .then((data) => {

        if (query === "") {
          setProducts(
            data.products || []
          );
        } else {
          setProducts(
            data.results || []
          );
        }

        setLoading(false);

      })
      .catch((error) => {

        console.error(error);

        setLoading(false);

      });

  }, [query, selectedBrand, selectedRating]);

  // No local filtering needed anymore, backend handles it!
  const filteredProducts = products;

  return (
    <div className="results-page">

      <Navbar />

      <h1 className="results-title">
        {query === ""
          ? "All Products"
          : `Results for "${query}"`}
      </h1>

      <p
        style={{
          textAlign: "center",
          marginBottom: "10px"
        }}
      >
        {filteredProducts.length} Products Found
      </p>

      <div className="results-layout">

        <Filters
          selectedBrand={selectedBrand}
          setSelectedBrand={setSelectedBrand}
          selectedRating={selectedRating}
          setSelectedRating={setSelectedRating}
        />

        <div className="products-container">

          {loading ? (

            <h2>Searching...</h2>

          ) : filteredProducts.length === 0 ? (

            <h2>No Products Found</h2>

          ) : (

            filteredProducts.map(
              (product) => (

                <ProductCard
                  key={product.id}
                  product={product}
                />

              )
            )

          )}

        </div>

      </div>

    </div>
  );
}

export default SearchResults;