import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api";

export default function SessionsPage() {
  const [requests, setRequests] = useState([]);
  const [sessions, setSessions] = useState([]);
  const navigate = useNavigate();

  const load = async () => {
    const reqRes = await apiFetch("/jit-requests");
    const sessRes = await apiFetch("/sessions");
    if (reqRes.ok) {
      setRequests(await reqRes.json());
    }
    if (sessRes.ok) {
      setSessions(await sessRes.json());
    }
  };

  useEffect(() => {
    load();
  }, []);

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
    }
  };

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
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {requests.filter((item) => item.status === "APPROVED").map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.asset_id}</td>
                <td>{item.role_id}</td>
                <td>{item.status}</td>
                <td><button onClick={() => startSession(item.id)}>Start</button></td>
              </tr>
            ))}
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
                  <button onClick={() => navigate(`/replay/${session.id}`)}>Replay</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
