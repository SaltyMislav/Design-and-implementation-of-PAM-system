import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { NavLink, Route, Routes, useNavigate } from "react-router-dom";
import API_URL, { apiFetch, clearTokens, getTokens, setTokens } from "./api";
import LoginPage from "./pages/LoginPage";
import AssetsPage from "./pages/AssetsPage";
import JitRequestPage from "./pages/JitRequestPage";
import ApprovalsPage from "./pages/ApprovalsPage";
import SessionsPage from "./pages/SessionsPage";
import TerminalPage from "./pages/TerminalPage";
import ReplayPage from "./pages/ReplayPage";
import MfaPage from "./pages/MfaPage";
import AuditPage from "./pages/AuditPage";
import ToastProvider from "./components/ToastProvider";

const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}

function Layout({ children }) {
  const auth = useAuth();
  return (
    <div className="app">
      <aside className="sidebar">
        <h1>PAM Demo</h1>
        <nav className="nav">
          <NavLink to="/assets">Assets</NavLink>
          <NavLink to="/jit">Request Access</NavLink>
          <NavLink to="/approvals">Approvals</NavLink>
          <NavLink to="/sessions">Sessions</NavLink>
          <NavLink to="/mfa">Admin MFA</NavLink>
          <NavLink to="/audit">Audit Logs</NavLink>
        </nav>
        <div>
          <button className="secondary" onClick={auth.logout}>Log out</button>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });
  const navigate = useNavigate();

  const auth = useMemo(() => ({
    user,
    async login(email, password) {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      if (!response.ok) {
        throw new Error("Login failed");
      }
      const data = await response.json();
      setTokens(data.access_token, data.refresh_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      setUser(data.user);
      navigate("/assets");
    },
    logout() {
      clearTokens();
      localStorage.removeItem("user");
      setUser(null);
      navigate("/");
    },
    async refreshUser() {
      const response = await apiFetch("/auth/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: getTokens().refresh })
      });
      if (response.ok) {
        const data = await response.json();
        setTokens(data.access_token, data.refresh_token);
        localStorage.setItem("user", JSON.stringify(data.user));
        setUser(data.user);
      }
    }
  }), [user, navigate]);

  useEffect(() => {
    const handler = () => {
      if (user) {
        auth.logout();
      } else {
        clearTokens();
        localStorage.removeItem("user");
        navigate("/");
      }
    };
    window.addEventListener("auth:unauthorized", handler);
    return () => window.removeEventListener("auth:unauthorized", handler);
  }, [auth, navigate, user]);

  return (
    <AuthContext.Provider value={auth}>
      <ToastProvider>
        <Routes>
          <Route path="/" element={user ? <Layout><AssetsPage /></Layout> : <LoginPage />} />
          <Route path="/assets" element={user ? <Layout><AssetsPage /></Layout> : <LoginPage />} />
          <Route path="/jit" element={user ? <Layout><JitRequestPage /></Layout> : <LoginPage />} />
          <Route path="/approvals" element={user ? <Layout><ApprovalsPage /></Layout> : <LoginPage />} />
          <Route path="/sessions" element={user ? <Layout><SessionsPage /></Layout> : <LoginPage />} />
          <Route path="/sessions/:id" element={user ? <Layout><TerminalPage /></Layout> : <LoginPage />} />
          <Route path="/replay/:id" element={user ? <Layout><ReplayPage /></Layout> : <LoginPage />} />
          <Route path="/mfa" element={user ? <Layout><MfaPage /></Layout> : <LoginPage />} />
          <Route path="/audit" element={user ? <Layout><AuditPage /></Layout> : <LoginPage />} />
        </Routes>
      </ToastProvider>
    </AuthContext.Provider>
  );
}
