import { useState } from "react";
import { supabase } from "../lib/supabase";

function Login({ onSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const login = async () => {
    setLoading(true);
    setError(null);

    console.log("Trying login with:", email);

    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    console.log("Supabase response:", { data, error });

    setLoading(false);

    if (error) {
      console.error("Login error:", error.message);
      setError(error.message);
      return;
    }

    if (!data?.session) {
      console.error("No session returned:", data);
      return;
    }

    const token = data.session.access_token;

    console.log("🔥 JWT TOKEN:", token);

    localStorage.setItem("access_token", token);

    onSuccess?.(token);
  };

  return (
    <div style={{ padding: 20, maxWidth: 300 }}>
      <h2>Login</h2>

      <input
        placeholder="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{ display: "block", marginBottom: 10, width: "100%" }}
      />

      <input
        placeholder="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ display: "block", marginBottom: 10, width: "100%" }}
      />

      <button onClick={login} disabled={loading}>
        {loading ? "Logging in..." : "Login"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default Login;