import React, { useEffect, useState } from "react";
import { apiFetch, getErrorMessage } from "../api";
import { useAuth } from "../App";
import { useToast } from "../components/ToastProvider";

export default function AssetsPage() {
  const { user } = useAuth();
  const { addToast } = useToast();
  const [assets, setAssets] = useState([]);
  const [form, setForm] = useState({ name: "", host: "", port: 2222, type: "ssh" });
  const [cred, setCred] = useState({ assetId: "", username: "", password: "" });
  const [assetMfaCode, setAssetMfaCode] = useState("");
  const [credMfaCode, setCredMfaCode] = useState("");

  const loadAssets = async () => {
    const response = await apiFetch("/assets");
    if (response.ok) {
      setAssets(await response.json());
    }
  };

  useEffect(() => {
    loadAssets();
  }, []);

  const createAsset = async (event) => {
    event.preventDefault();
    const response = await apiFetch("/assets", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-MFA-TOTP": assetMfaCode
      },
      body: JSON.stringify({
        name: form.name,
        host: form.host,
        port: Number(form.port),
        type: form.type
      })
    });
    if (response.ok) {
      setForm({ name: "", host: "", port: 2222, type: "ssh" });
      loadAssets();
      addToast("Asset created.", "success");
      setAssetMfaCode("");
    } else {
      addToast(await getErrorMessage(response), "error");
    }
  };

  const setCredential = async (event) => {
    event.preventDefault();
    const response = await apiFetch(`/assets/${cred.assetId}/credential`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-MFA-TOTP": credMfaCode
      },
      body: JSON.stringify({ username: cred.username, password: cred.password })
    });
    if (response.ok) {
      setCred({ assetId: "", username: "", password: "" });
      addToast("Credential saved to Vault.", "success");
      setCredMfaCode("");
    } else {
      addToast(await getErrorMessage(response), "error");
    }
  };

  return (
    <div>
      <div className="card">
        <h2>Assets</h2>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Host</th>
              <th>Port</th>
            </tr>
          </thead>
          <tbody>
            {assets.map((asset) => (
              <tr key={asset.id}>
                <td>{asset.id}</td>
                <td>{asset.name}</td>
                <td>{asset.host}</td>
                <td>{asset.port}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {user?.is_admin && (
        <div className="card">
          <h3>Create Asset (Admin + MFA)</h3>
          <form onSubmit={createAsset}>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Name" />
            <input value={form.host} onChange={(e) => setForm({ ...form, host: e.target.value })} placeholder="Host" />
            <input value={form.port} onChange={(e) => setForm({ ...form, port: e.target.value })} placeholder="Port" />
            <input value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })} placeholder="Type" />
            <input value={assetMfaCode} onChange={(e) => setAssetMfaCode(e.target.value)} placeholder="MFA Code" />
            <button type="submit">Create</button>
          </form>
        </div>
      )}
      {user?.is_admin && (
        <div className="card">
          <h3>Store Credential in Vault (Admin + MFA)</h3>
          <form onSubmit={setCredential}>
            <select value={cred.assetId} onChange={(e) => setCred({ ...cred, assetId: e.target.value })}>
              <option value="">Select asset</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>{asset.name} (ID {asset.id})</option>
              ))}
            </select>
            <input value={cred.username} onChange={(e) => setCred({ ...cred, username: e.target.value })} placeholder="Username" />
            <input type="password" value={cred.password} onChange={(e) => setCred({ ...cred, password: e.target.value })} placeholder="Password" />
            <input value={credMfaCode} onChange={(e) => setCredMfaCode(e.target.value)} placeholder="MFA Code" />
            <button type="submit">Save Credential</button>
          </form>
        </div>
      )}
    </div>
  );
}
