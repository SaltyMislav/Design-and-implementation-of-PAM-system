import React, { useState } from "react";
import QRCode from "qrcode";
import { apiFetch } from "../api";
import { useAuth } from "../App";

export default function MfaPage() {
  const { user } = useAuth();
  const [secret, setSecret] = useState("");
  const [otpauth, setOtpauth] = useState("");
  const [qrUrl, setQrUrl] = useState("");
  const [code, setCode] = useState("");

  const setupMfa = async () => {
    const response = await apiFetch("/auth/mfa/setup", { method: "POST" });
    if (response.ok) {
      const data = await response.json();
      setSecret(data.secret);
      setOtpauth(data.otpauth_url);
      const url = await QRCode.toDataURL(data.otpauth_url);
      setQrUrl(url);
    }
  };

  const enableMfa = async () => {
    const response = await apiFetch("/auth/mfa/enable", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code })
    });
    if (response.ok) {
      setCode("");
    }
  };

  if (!user?.is_admin) {
    return <div className="notice">Admin access required.</div>;
  }

  return (
    <div className="card">
      <h2>Admin MFA Setup</h2>
      <button onClick={setupMfa}>Generate Secret</button>
      {secret && (
        <div>
          <p>Secret: {secret}</p>
          {qrUrl && <img src={qrUrl} alt="MFA QR" style={{ maxWidth: 200 }} />}
          <p>Authenticator URL: {otpauth}</p>
        </div>
      )}
      <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="Enter MFA code" />
      <button onClick={enableMfa}>Enable MFA</button>
    </div>
  );
}
