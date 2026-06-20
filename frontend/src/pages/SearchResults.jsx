import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";

import Navbar from "../components/Navbar";
import Filters from "../components/Filters";
import ProductCard from "../components/ProductCard";

import API_BASE_URL from "../config";

function SearchResults() {

  const [searchParams] =
    useSearchParams();

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

    fetch(
      `${API_BASE_URL}/search?q=${query}`,
      {
        headers: {
          "ngrok-skip-browser-warning":
            "true"
        }
      }
    )
      .then((response) =>
        response.json()
      )
      .then((data) => {

        setProducts(
          data.results || []
        );

        setLoading(false);

      })
      .catch((error) => {

        console.error(error);

        setLoading(false);

      });

  }, [query]);

  const filteredProducts =
    products.filter((product) => {

      const brandMatch =
        selectedBrand === "" ||
        product.brand === selectedBrand;

      const ratingMatch =
        product.rating >=
        selectedRating;

      return (
        brandMatch &&
        ratingMatch
      );
    });

  return (
    <div className="results-page">

      <Navbar />

      <h1 className="results-title">
        Results for "{query}"
      </h1>

      <div className="results-layout">

        <Filters
          selectedBrand={
            selectedBrand
          }
          setSelectedBrand={
            setSelectedBrand
          }
          selectedRating={
            selectedRating
          }
          setSelectedRating={
            setSelectedRating
          }
        />

        <div className="products-container">

          {loading ? (

            <h2>
              Loading...
            </h2>

          ) : (

            filteredProducts.map(
              (product) => (

                <ProductCard
                  key={
                    product.id
                  }
                  product={
                    product
                  }
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