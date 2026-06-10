import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

function CustomerProtectedRoute({ children }) {
  const [authorized, setAuthorized] = useState(null);

  useEffect(() => {
    fetch("/api/customer", {
      credentials: "include",
    })
      .then((res) => {
        if (res.ok) {
          setAuthorized(true);
        } else {
          setAuthorized(false);
        }
      })
      .catch(() => {
        setAuthorized(false);
      });
  }, []);

  if (authorized === null) {
    return <h2>Loading...</h2>;
  }

  if (!authorized) {
    return <Navigate to="/login" />;
  }

  return children;
}

export default CustomerProtectedRoute;