import { useState } from "react";
import { useNavigate } from "react-router-dom";

function SearchBar() {

  const [query, setQuery] = useState("");

  const navigate = useNavigate();

  const handleSearch = () => {

    if (!query.trim()) return;

    navigate(
      `/results?q=${encodeURIComponent(query)}`
    );

  };

  return (
    <div className="search-container">

      <input
        type="text"
        placeholder="Search Nike shoes, AirPods, laptops..."
        className="search-input"
        value={query}
        onChange={(e) =>
          setQuery(e.target.value)
        }
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