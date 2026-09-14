import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await api.post("/auth/login", { email, password });
      localStorage.setItem("access_token", response.data.access_token);
      navigate("/dashboard");
    } catch {
      setError("Unable to log in. Check your email and password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page auth-page">
      <h1>VerifyAI</h1>
      <form className="card form" onSubmit={handleSubmit}>
        <h2>Log in</h2>
        <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
        <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>{loading ? "Logging in..." : "Log in"}</button>
        <p>Need an account? <Link to="/register">Register</Link></p>
      </form>
    </main>
  );
}

export default Login;
