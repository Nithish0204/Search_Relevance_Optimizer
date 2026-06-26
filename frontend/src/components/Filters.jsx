function Filters({
  brands = [],
  selectedBrand,
  setSelectedBrand,
  selectedRating,
  setSelectedRating
}) {
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
            checked={selectedBrand === brand}
            onChange={() => setSelectedBrand(brand)}
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