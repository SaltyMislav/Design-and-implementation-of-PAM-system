import React, { useEffect, useState } from "react";
import { apiFetch, getErrorMessage } from "../api";
import { useToast } from "../components/ToastProvider";

export default function JitRequestPage() {
  const { addToast } = useToast();
  const [assets, setAssets] = useState([]);
  const [roles, setRoles] = useState([]);
  const [form, setForm] = useState({ asset_id: "", role_id: "", reason: "", duration_minutes: 30 });

  useEffect(() => {
    const load = async () => {
      const assetsResponse = await apiFetch("/assets");
      const rolesResponse = await apiFetch("/roles");
      if (assetsResponse.ok) {
        setAssets(await assetsResponse.json());
      }
      if (rolesResponse.ok) {
        setRoles(await rolesResponse.json());
      }
    };
    load();
  }, []);

  const submit = async (event) => {
    event.preventDefault();
    const response = await apiFetch("/jit-requests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        asset_id: Number(form.asset_id),
        role_id: Number(form.role_id),
        reason: form.reason,
        duration_minutes: Number(form.duration_minutes)
      })
    });
    if (response.ok) {
      setForm({ asset_id: "", role_id: "", reason: "", duration_minutes: 30 });
      addToast("JIT request submitted.", "success");
    } else {
      addToast(await getErrorMessage(response), "error");
    }
  };

  return (
    <div className="card">
      <h2>Request Just-In-Time Access</h2>
      <form onSubmit={submit}>
        <select value={form.asset_id} onChange={(e) => setForm({ ...form, asset_id: e.target.value })}>
          <option value="">Select asset</option>
          {assets.map((asset) => (
            <option key={asset.id} value={asset.id}>{asset.name}</option>
          ))}
        </select>
        <select value={form.role_id} onChange={(e) => setForm({ ...form, role_id: e.target.value })}>
          <option value="">Select role</option>
          {roles.map((role) => (
            <option key={role.id} value={role.id}>{role.name}</option>
          ))}
        </select>
        <textarea value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} placeholder="Reason" />
        <input value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })} placeholder="Duration (minutes)" />
        <button type="submit">Submit Request</button>
      </form>
    </div>
  );
}
