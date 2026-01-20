import React, { useState } from "react";
import { useAuth } from "../App";
import { useToast } from "../components/ToastProvider";

export default function LoginPage() {
  const auth = useAuth();
  const { addToast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await auth.login(email, password);
    } catch (err) {
      addToast("Login failed. Check credentials.", "error");
    }
  };

  return (
    <div className="main">
      <div className="card" style={{ maxWidth: 420, margin: "80px auto" }}>
        <h2>Sign in</h2>
        <form onSubmit={handleSubmit}>
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
          />
          <button type="submit">Login</button>
        </form>
      </div>
    </div>
  );
}
