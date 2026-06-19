import { useNavigate } from "react-router-dom";

function SearchBar() {
  const navigate = useNavigate();

  const handleSearch = () => {
    navigate("/results");
  };

  return (
    <div className="search-container">

      <input
        type="text"
        placeholder="Search Nike shoes, AirPods, laptops..."
        className="search-input"
      />

      <button
        className="search-btn"
        onClick={handleSearch}
      >
        Search
      </button>

    </div>
  );
}

export default SearchBar;