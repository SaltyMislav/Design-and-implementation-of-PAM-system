import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API_URL, { apiFetch, getErrorMessage } from "../api";
import { useToast } from "../components/ToastProvider";
import { useAuth } from "../App";

export default function SessionsPage() {
  const { addToast } = useToast();
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [assets, setAssets] = useState([]);
  const [roles, setRoles] = useState([]);
  const [commandLogs, setCommandLogs] = useState({});
  const [selectedSession, setSelectedSession] = useState(null);
  const [commandLoading, setCommandLoading] = useState(false);
  const navigate = useNavigate();

  const load = async () => {
    const reqRes = await apiFetch("/jit-requests");
    const sessRes = await apiFetch("/sessions");
    const assetsRes = await apiFetch("/assets");
    const rolesRes = await apiFetch("/roles");
    if (reqRes.ok) {
      setRequests(await reqRes.json());
    }
    if (sessRes.ok) {
      setSessions(await sessRes.json());
    }
    if (assetsRes.ok) {
      setAssets(await assetsRes.json());
    }
    if (rolesRes.ok) {
      setRoles(await rolesRes.json());
    }
  };

  useEffect(() => {
    load();
    if (!user?.is_admin) {
      return undefined;
    }
    const wsUrl = API_URL.replace(/^http/, "ws") + "/ws/updates";
    const socket = new WebSocket(wsUrl);
    socket.onmessage = () => load();
    socket.onerror = () => addToast("Live updates disconnected.", "error");
    return () => socket.close();
  }, [user?.is_admin]);

  const startSession = async (jitId) => {
    const response = await apiFetch("/sessions/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jit_request_id: jitId })
    });
    if (response.ok) {
      const data = await response.json();
      sessionStorage.setItem(`session_token_${data.session_id}`, data.session_token);
      sessionStorage.setItem(`session_ws_${data.session_id}`, data.websocket_url);
      navigate(`/sessions/${data.session_id}`);
    } else {
      addToast(await getErrorMessage(response), "error");
    }
  };

  const loadCommands = async (sessionId) => {
    setCommandLoading(true);
    const response = await apiFetch(`/sessions/${sessionId}/commands?limit=200`);
    if (response.ok) {
      const data = await response.json();
      setCommandLogs((current) => ({ ...current, [sessionId]: data }));
      setSelectedSession(sessionId);
    } else {
      addToast(await getErrorMessage(response), "error");
    }
    setCommandLoading(false);
  };

  const selectedCommands = selectedSession ? commandLogs[selectedSession] || [] : [];

  const assetMap = Object.fromEntries(assets.map((asset) => [asset.id, asset]));
  const roleMap = Object.fromEntries(roles.map((role) => [role.id, role]));

  return (
    <div>
      <div className="card">
        <h2>Approved JIT Requests</h2>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Asset</th>
              <th>Role</th>
              <th>Expires</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {requests
              .filter((item) => item.status === "APPROVED")
              .filter((item) => (user ? item.user_id === user.id : true))
              .sort((a, b) => new Date(a.expires_at || 0) - new Date(b.expires_at || 0))
              .map((item) => {
                const asset = assetMap[item.asset_id];
                const role = roleMap[item.role_id];
                return (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{asset ? `${asset.name} (ID ${asset.id})` : `ID ${item.asset_id}`}</td>
                    <td>{role ? role.name : `ID ${item.role_id}`}</td>
                    <td>{item.expires_at ? new Date(item.expires_at).toLocaleString() : "-"}</td>
                    <td>{item.status}</td>
                    <td><button onClick={() => startSession(item.id)}>Start</button></td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>
      <div className="card">
        <h2>Sessions</h2>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>JIT Request</th>
              <th>Status</th>
              <th>Last Command</th>
              <th>Commands</th>
              <th>Replay</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session) => (
              <tr key={session.id}>
                <td>{session.id}</td>
                <td>{session.jit_request_id}</td>
                <td>{session.status}</td>
                <td>
                  {(commandLogs[session.id] && commandLogs[session.id].length > 0)
                    ? commandLogs[session.id][commandLogs[session.id].length - 1].line
                    : "-"}
                </td>
                <td>
                  <button className="secondary" onClick={() => loadCommands(session.id)}>View</button>
                </td>
                <td>
                  <button onClick={() => navigate(`/replay/${session.id}`)}>Replay</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {selectedSession && (
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3>Command Log for Session {selectedSession}</h3>
            <button className="secondary" onClick={() => setSelectedSession(null)}>Close</button>
          </div>
          {commandLoading ? (
            <p>Loading commands...</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Command</th>
                </tr>
              </thead>
              <tbody>
                {selectedCommands.map((entry, index) => (
                  <tr key={`${entry.ts}-${index}`}>
                    <td>{new Date(entry.ts * 1000).toLocaleString()}</td>
                    <td>{entry.line}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {selectedCommands.length === 0 && !commandLoading && (
            <div className="notice">No command log entries for this session.</div>
          )}
        </div>
      )}
    </div>
  );
}
