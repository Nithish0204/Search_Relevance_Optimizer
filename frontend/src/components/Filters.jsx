import { useState, useEffect } from "react";
import API_BASE_URL from "../config";

function Filters({
  selectedBrand,
  setSelectedBrand,
  selectedRating,
  setSelectedRating
}) {
  const [brands, setBrands] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/stats`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.brands) {
          // Capitalize first letter of brands for display
          const formattedBrands = data.brands.map(
            (b) => b.charAt(0).toUpperCase() + b.slice(1)
          );
          setBrands(formattedBrands);
        }
      })
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className="filter-sidebar">

      <h2>Filters</h2>

      <h3>Brand</h3>

      <label>
        <input
          type="radio"
          name="brand"
          checked={selectedBrand === ""}
          onChange={() => setSelectedBrand("")}
        />
        All Brands
      </label>

      {brands.map((brand) => (
        <label key={brand}>
          <input
            type="radio"
            name="brand"
            checked={selectedBrand === brand.toLowerCase()}
            onChange={() => setSelectedBrand(brand.toLowerCase())}
          />
          {brand}
        </label>
      ))}

      <h3>Rating</h3>

      <label>
        <input
          type="radio"
          name="rating"
          checked={selectedRating === 4}
          onChange={() => setSelectedRating(4)}
        />
        4★ & Above
      </label>

      <label>
        <input
          type="radio"
          name="rating"
          checked={selectedRating === 0}
          onChange={() => setSelectedRating(0)}
        />
        All Ratings
      </label>

    </div>
  );
}

export default Filters;