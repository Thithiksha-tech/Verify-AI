import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/auth/register", form);
      navigate("/");
    } catch {
      setError("Unable to register. The email may already be in use.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page auth-page">
      <h1>VerifyAI</h1>
      <form className="card form" onSubmit={handleSubmit}>
        <h2>Create account</h2>
        <label>Name<input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required /></label>
        <label>Email<input type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required /></label>
        <label>Password<input type="password" minLength={8} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required /></label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>{loading ? "Registering..." : "Register"}</button>
        <p>Already registered? <Link to="/">Log in</Link></p>
      </form>
    </main>
  );
}

export default Register;
