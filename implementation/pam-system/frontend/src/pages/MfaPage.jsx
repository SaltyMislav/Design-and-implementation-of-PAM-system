import React, { useState } from "react";
import QRCode from "qrcode";
import { apiFetch, getErrorMessage } from "../api";
import { useAuth } from "../App";
import { useToast } from "../components/ToastProvider";

export default function MfaPage() {
  const { user, refreshUser } = useAuth();
  const { addToast } = useToast();
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
      addToast("MFA secret generated.", "success");
    } else {
      addToast(await getErrorMessage(response), "error");
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
      setSecret("");
      setOtpauth("");
      setQrUrl("");
      addToast("MFA enabled.", "success");
      await refreshUser();
    } else {
      addToast(await getErrorMessage(response), "error");
    }
  };

  const disableMfa = async () => {
    const response = await apiFetch("/auth/mfa/disable", {
      method: "POST",
      headers: { "X-MFA-TOTP": code }
    });
    if (response.ok) {
      setCode("");
      setSecret("");
      setOtpauth("");
      setQrUrl("");
      addToast("MFA disabled.", "success");
      await refreshUser();
    } else {
      addToast(await getErrorMessage(response), "error");
    }
  };

  if (!user?.is_admin) {
    return <div className="notice">Admin access required.</div>;
  }

  return (
    <div className="card">
      <h2>Admin MFA Setup</h2>
      {user?.mfa_enabled ? (
        <div className="notice">MFA is enabled. Disable it to enroll a new device.</div>
      ) : (
        <button onClick={setupMfa}>Generate Secret</button>
      )}
      {secret && (
        <div>
          <p>Secret: {secret}</p>
          {qrUrl && <img src={qrUrl} alt="MFA QR" style={{ maxWidth: 200 }} />}
          <p>Authenticator URL: {otpauth}</p>
        </div>
      )}
      <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="Enter MFA code" />
      {!user?.mfa_enabled && <button onClick={enableMfa}>Enable MFA</button>}
      {user?.mfa_enabled && <button className="secondary" onClick={disableMfa}>Disable MFA</button>}
    </div>
  );
}
