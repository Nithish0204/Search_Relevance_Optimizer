function Filters({
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
          onChange={() => setSelectedBrand("")}
        />
        All Brands
      </label>

      <label>
        <input
          type="radio"
          name="brand"
          onChange={() => setSelectedBrand("Nike")}
        />
        Nike
      </label>

      <label>
        <input
          type="radio"
          name="brand"
          onChange={() => setSelectedBrand("Sony")}
        />
        Sony
      </label>

      <label>
        <input
          type="radio"
          name="brand"
          onChange={() => setSelectedBrand("Adidas")}
        />
        Adidas
      </label>

      <h3>Rating</h3>

      <label>
        <input
          type="radio"
          name="rating"
          onChange={() => setSelectedRating(4)}
        />
        4★ & Above
      </label>

      <label>
        <input
          type="radio"
          name="rating"
          onChange={() => setSelectedRating(0)}
        />
        All Ratings
      </label>

    </div>
  );
}

export default Filters;