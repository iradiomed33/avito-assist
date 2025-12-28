import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/auth";

export default function LoginPage() {
  const nav = useNavigate();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      await login(username, password);
      nav("/projects");
    } catch (e: any) {
      setErr(e?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: "40px auto", fontFamily: "Arial" }}>
      <h2>Avito Assist — Login</h2>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
        <label>
          Username
          <input
            style={{ width: "100%", padding: 10, marginTop: 6 }}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          />
        </label>

        <label>
          Password
          <input
            style={{ width: "100%", padding: 10, marginTop: 6 }}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </label>

        {err && (
          <div style={{ background: "#ffe5e5", padding: 10, borderRadius: 8 }}>
            {err}
          </div>
        )}

        <button disabled={loading} style={{ padding: 12, cursor: "pointer" }}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <div style={{ marginTop: 16, opacity: 0.75, fontSize: 12 }}>
        API base: {import.meta.env.VITE_API_BASE}
      </div>
    </div>
  );
}
