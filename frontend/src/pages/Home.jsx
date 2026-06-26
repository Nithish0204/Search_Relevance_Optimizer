import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import SearchBar from "../components/SearchBar";

function Home() {

  const navigate = useNavigate();

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

          <span
            onClick={() =>
              navigate("/results?q=Nike Shoes")
            }
            style={{ cursor: "pointer" }}
          >
            Nike Shoes
          </span>

          <span
            onClick={() =>
              navigate("/results?q=AirPods")
            }
            style={{ cursor: "pointer" }}
          >
            AirPods
          </span>

          <span
            onClick={() =>
              navigate("/results?q=Laptops")
            }
            style={{ cursor: "pointer" }}
          >
            Laptops
          </span>

          <span
            onClick={() =>
              navigate("/results?q=Smart Watches")
            }
            style={{ cursor: "pointer" }}
          >
            Smart Watches
          </span>

        </div>

      </div>

    </div>
  );
}

export default Home;