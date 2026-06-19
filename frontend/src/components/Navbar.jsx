import { useNavigate } from "react-router-dom";

function Navbar() {

  const navigate = useNavigate();

  return (
    <nav className="navbar">

      <div className="logo">
        Search Optimizer
      </div>

      <ul className="nav-links">
        <li>Home</li>
        <li>Products</li>
        <li>Analytics</li>
        <li>About</li>
      </ul>

      <button
        className="login-btn"
        onClick={() => navigate("/admin-login")}
      >
        Admin Login
      </button>

    </nav>
  );
}

export default Navbar;