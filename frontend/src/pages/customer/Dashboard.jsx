import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  const [customer, setCustomer] = useState(null);

  useEffect(() => {
    fetch("/api/customer", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setCustomer(data.customer);
      });
  }, []);

  const logout = async () => {
    await fetch("/api/logout", {
      method: "POST",
      credentials: "include",
    });

    navigate("/login");
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>Dashboard</h1>

      {customer && (
        <>
          <h3>{customer.name}</h3>

          <p>Email: {customer.email}</p>
          <p>Age: {customer.age}</p>
          <p>Gender: {customer.gender}</p>
          <p>Country: {customer.country}</p>
        </>
      )}

      <button onClick={logout}>
        Logout
      </button>
    </div>
  );
}

export default Dashboard;