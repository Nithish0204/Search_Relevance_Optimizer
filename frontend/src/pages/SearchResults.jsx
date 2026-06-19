import { useState } from "react";
import Navbar from "../components/Navbar";
import Filters from "../components/Filters";
import ProductCard from "../components/ProductCard";

function SearchResults() {

  const [selectedBrand, setSelectedBrand] = useState("");
  const [selectedRating, setSelectedRating] = useState(0);

  const products = [
    {
      id: 1,
      name: "Nike Air Max",
      price: 4999,
      rating: 4.5,
      brand: "Nike",
      stock: true,
      image:
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500"
    },

    {
      id: 2,
      name: "Boat Airdopes 141",
      price: 1299,
      rating: 4.2,
      brand: "Boat",
      stock: true,
      image:
        "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=500"
    },

    {
      id: 3,
      name: "Apple AirPods Pro",
      price: 24999,
      rating: 4.8,
      brand: "Apple",
      stock: true,
      image:
        "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500"
    }
  ];

  const filteredProducts = products.filter((product) => {

    const brandMatch =
      selectedBrand === "" ||
      product.brand === selectedBrand;

    const ratingMatch =
      product.rating >= selectedRating;

    return brandMatch && ratingMatch;
  });

  return (
    <div className="results-page">

      <Navbar />

      <h1 className="results-title">
        Search Results
      </h1>

      <div className="results-layout">

        <Filters
          selectedBrand={selectedBrand}
          setSelectedBrand={setSelectedBrand}
          selectedRating={selectedRating}
          setSelectedRating={setSelectedRating}
        />

        <div className="products-container">

          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
            />
          ))}

        </div>

      </div>

    </div>
  );
}

export default SearchResults;