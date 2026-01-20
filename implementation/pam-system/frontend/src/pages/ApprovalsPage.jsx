import React, { useEffect, useState } from "react";
import { apiFetch, getErrorMessage } from "../api";
import { useAuth } from "../App";
import { useToast } from "../components/ToastProvider";

export default function ApprovalsPage() {
  const { user } = useAuth();
  const { addToast } = useToast();
  const [requests, setRequests] = useState([]);
  const [mfaCode, setMfaCode] = useState("");

  const load = async () => {
    const response = await apiFetch("/jit-requests");
    if (response.ok) {
      setRequests(await response.json());
    }
  };

  useEffect(() => {
    load();
  }, []);

  const action = async (id, actionName) => {
    const response = await apiFetch(`/jit-requests/${id}/${actionName}`, {
      method: "POST",
      headers: { "X-MFA-TOTP": mfaCode }
    });
    if (response.ok) {
      load();
      addToast(`Request ${actionName}d.`, "success");
    } else {
      addToast(await getErrorMessage(response), "error");
    }
  };

  if (!user?.is_admin) {
    return <div className="notice">Admin access required.</div>;
  }

  return (
    <div className="card">
      <h2>Approvals Queue</h2>
      <input value={mfaCode} onChange={(e) => setMfaCode(e.target.value)} placeholder="MFA Code" />
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>User</th>
            <th>Asset</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {requests.filter((item) => item.status === "PENDING").map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.user_id}</td>
              <td>{item.asset_id}</td>
              <td>{item.role_id}</td>
              <td>{item.status}</td>
              <td>
                <button onClick={() => action(item.id, "approve")}>Approve</button>
                <button className="secondary" onClick={() => action(item.id, "deny")}>Deny</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
