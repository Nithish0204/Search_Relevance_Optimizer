import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import SearchBar from "../components/SearchBar";
import API_BASE_URL from "../config";

function Home() {

  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/stats`)
      .then((res) => res.json())
      .then((data) => {
        if (data.categories) {
          // Take up to 4 categories for the bubbles
          setCategories(data.categories.slice(0, 4));
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
          {categories.map((category) => (
            <span
              key={category}
              onClick={() =>
                navigate(`/results?q=${category}`)
              }
              style={{ cursor: "pointer" }}
            >
              {category}
            </span>
          ))}
        </div>

      </div>

    </div>
  );
}

export default Home;