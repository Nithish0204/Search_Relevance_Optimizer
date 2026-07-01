import { useNavigate, useLocation } from "react-router-dom";

function Navbar() {

  const navigate = useNavigate();
  const location = useLocation();

  return (
    <nav className="navbar">

      <div
  className="logo"
  onClick={() => navigate("/")}
  style={{ cursor: "pointer" }}
>
  🛍️ SmartSearch
</div>

      <ul className="nav-links">

        <li
          onClick={() =>
            navigate("/results?q=")
          }
          style={{
            cursor: "pointer"
          }}
        >
          📦 Products
        </li>

      </ul>

      {location.pathname === "/" && (
        <button
          className="login-btn"
          onClick={() =>
            navigate("/admin-login")
          }
        >
          Admin Login
        </button>
      )}

    </nav>
  );
}

export default Navbar;