import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";

function Login() {
    const navigate = useNavigate();

    const [form, setForm] = useState({
        email: "",
        password: "",
    });

    const [message, setMessage] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        const response = await fetch("/api/login", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(form),
        });

        if (!response.ok) {
            return;
        }

        const meResponse = await fetch("/api/me", {
            credentials: "include",
        });

        const me = await meResponse.json();

        if (me.role === "admin") {
            navigate("/admin/dashboard");
        } else {
            navigate("/customer/dashboard");
        }
    };

    return (
        <div style={{ padding: "50px" }}>
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <input
                        type="email"
                        placeholder="Email"
                        value={form.email}
                        onChange={(e) =>
                            setForm({
                                ...form,
                                email: e.target.value,
                            })}
                    />
                </div>
                <br />
                <div>
                    <input
                        type="password"
                        placeholder="Password"
                        value={form.password}
                        onChange={(e) =>
                            setForm({
                                ...form,
                                password: e.target.value,
                            })
                        }
                    />
                </div>
                <br />
                <button type="submit">
                    Login
                </button>
                <p>
                    don't have an account yet?{" "}
                    <Link to="/register">
                        Register
                    </Link>
                </p>
            </form>
            <p>{message}</p>
        </div>
    );
}

export default Login;