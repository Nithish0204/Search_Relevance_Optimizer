import { Link } from "react-router-dom";

function AdminDashboard() {
  return (
    <div className="admin-dashboard">

      <div className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <p>
          Manage products, inventory and search system.
        </p>
      </div>

      <div className="dashboard-cards">

        <Link
          to="/admin/add-product"
          className="dashboard-card"
        >
          <h2>➕ Add Product</h2>

          <p>
            Add new products to the database.
          </p>
        </Link>

        <Link
          to="/admin/manage-products"
          className="dashboard-card"
        >
          <h2>📦 Manage Products</h2>

          <p>
            View, edit and delete products.
          </p>
        </Link>

      </div>

    </div>
  );
}

export default AdminDashboard;