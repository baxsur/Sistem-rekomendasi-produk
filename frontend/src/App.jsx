import { Routes, Route } from "react-router-dom";

import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";

import Dashboard from "./pages/customer/Dashboard";
// import Profile from "./pages/customer/Profile";

import AdminDashboard from "./pages/admin/Dashboard";
// import ProductManagement from "./pages/admin/ProductManagement";

import CustomerProtectedRoute from "./components/CustomerProtectedRoute";
// import AdminProtectedRoute from "./components/AdminProtectedRoute";

function App() {
  return (
    <Routes>

      {/* PUBLIC */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* CUSTOMER */}
      <Route
        path="/customer/dashboard"
        element={
          <CustomerProtectedRoute>
            <Dashboard />
          </CustomerProtectedRoute>
        }
      />

      {/* <Route
        path="/profile"
        element={
          <CustomerProtectedRoute>
            <Profile />
          </CustomerProtectedRoute>
        }
      /> */}

      {/* ADMIN */}
      <Route
        path="/admin/dashboard"
        element={
          // <AdminProtectedRoute>
            <AdminDashboard />
          // </AdminProtectedRoute>
        }
      />

      {/* <Route
        path="/admin/products"
        element={
          <AdminProtectedRoute>
            <ProductManagement />
          </AdminProtectedRoute>
        }
      /> */}

    </Routes>
  );
}

export default App;