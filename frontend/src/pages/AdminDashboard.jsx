import { Link, useNavigate } from "react-router-dom";

function AdminDashboard() {

  const navigate = useNavigate();

  const handleLogout = () => {

    localStorage.removeItem(
      "adminLoggedIn"
    );

    navigate("/admin-login");
  };

  return (
    <div className="admin-dashboard">

      <div className="dashboard-header">

        <div>
          <h1>Admin Dashboard</h1>

          <p>
            Manage products and inventory.
          </p>
        </div>

        <button
          className="delete-btn"
          onClick={handleLogout}
        >
          Logout
        </button>

      </div>

      <div className="dashboard-cards">

        <Link
          to="/admin/add-product"
          className="dashboard-card"
        >
          <h2>➕ Add Product</h2>

          <p>
            Add products to database.
          </p>
        </Link>

        <Link
          to="/admin/manage-products"
          className="dashboard-card"
        >
          <h2>📦 Manage Products</h2>

          <p>
            View and delete products.
          </p>
        </Link>

      </div>

    </div>
  );
}

export default AdminDashboard;