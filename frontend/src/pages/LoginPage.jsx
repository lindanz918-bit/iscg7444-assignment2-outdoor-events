import { useState } from "react";
import { login, setToken } from "../api";

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await login(email, password);
      setToken(data.access_token);
      onLogin(data.user);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        maxWidth: "320px",
        margin: "40px auto",
        display: "flex",
        flexDirection: "column",
        gap: "10px",
      }}
    >
      <h3>Admin Login</h3>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit">Login</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </form>
  );
}