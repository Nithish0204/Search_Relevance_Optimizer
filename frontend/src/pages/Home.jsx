import Navbar from "../components/Navbar";
import SearchBar from "../components/SearchBar";

function Home() {
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
          <span>Nike Shoes</span>
          <span>AirPods</span>
          <span>Laptops</span>
          <span>Smart Watches</span>
        </div>

      </div>

    </div>
  );
}

export default Home;