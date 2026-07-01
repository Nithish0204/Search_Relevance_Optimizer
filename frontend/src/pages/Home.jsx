import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import SearchBar from "../components/SearchBar";
import API_BASE_URL from "../config";

function Home() {

  const navigate = useNavigate();

  const [popularCategories,
    setPopularCategories] = useState([]);

  useEffect(() => {

    fetch(`${API_BASE_URL}/stats`, {
      headers: {
        "ngrok-skip-browser-warning":
          "true"
      }
    })
      .then((res) => res.json())
      .then((data) => {

        if (data.categories) {

          const formatted =
            data.categories
              .slice(0, 8)
              .map(
                (c) =>
                  c.charAt(0).toUpperCase() +
                  c.slice(1)
              );

          setPopularCategories(
            formatted
          );

        }

      })
      .catch((err) =>
        console.error(err)
      );

  }, []);

  return (

    <div className="home">

      <Navbar />

      <div className="hero">

        <div className="hero-badge">
          🚀 AI Powered Product Search
        </div>

        <h1 className="title">
          Find Products Smarter
        </h1>

        <p className="subtitle">
          NLP + Elasticsearch + Hybrid Ranking
        </p>

        <SearchBar />

        <div className="popular-searches">

          <h3 className="popular-title">
            🔥 Trending Categories
          </h3>

          <div className="category-grid">

            {popularCategories.map(
              (cat) => (

                <div
                  key={cat}
                  className="category-card"
                  onClick={() =>
                    navigate(
                      `/results?q=${encodeURIComponent(
                        cat
                      )}`
                    )
                  }
                >

                  <div className="category-icon">

                    {cat.toLowerCase().includes("shoe")
                      ? "👟"
                      : cat.toLowerCase().includes("elect")
                      ? "📱"
                      : cat.toLowerCase().includes("cloth")
                      ? "👕"
                      : cat.toLowerCase().includes("watch")
                      ? "⌚"
                      : cat.toLowerCase().includes("laptop")
                      ? "💻"
                      : cat.toLowerCase().includes("book")
                      ? "📚"
                      : cat.toLowerCase().includes("beauty")
                      ? "💄"
                      : cat.toLowerCase().includes("sport")
                      ? "⚽"
                      : "🛍️"}

                  </div>

                  <p>{cat}</p>

                </div>

              )
            )}

          </div>

        </div>

      </div>

    </div>

  );
}

export default Home;