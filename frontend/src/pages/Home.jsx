import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import SearchBar from "../components/SearchBar";
import API_BASE_URL from "../config";

function Home() {

  const navigate = useNavigate();
  const [popularCategories, setPopularCategories] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/stats`, {
      headers: {
        "ngrok-skip-browser-warning": "true"
      }
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.categories) {
          // Capitalize first letter of categories and take top 4
          const formatted = data.categories
            .slice(0, 4)
            .map((c) => c.charAt(0).toUpperCase() + c.slice(1));
          setPopularCategories(formatted);
        }
      })
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className="home">

      <Navbar />

      <div className="hero">

        <h1 className="title">
          Search Relevance Optimizer
        </h1>

        <p className="subtitle">
          Intelligent E-Commerce Search using NLP, Elasticsearch and Smart Ranking
        </p>

        <SearchBar />

        <div className="popular-searches">

          {popularCategories.map((cat) => (
            <span
              key={cat}
              onClick={() => navigate(`/results?q=${encodeURIComponent(cat)}`)}
              style={{ cursor: "pointer" }}
            >
              {cat}
            </span>
          ))}

        </div>

      </div>

    </div>
  );
}

export default Home;