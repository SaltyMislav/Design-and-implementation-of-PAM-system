import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import { apiFetch } from "../api";
import "xterm/css/xterm.css";

function decodeBase64(data) {
  return Uint8Array.from(atob(data), (c) => c.charCodeAt(0));
}

export default function ReplayPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const termRef = useRef(null);
  const timersRef = useRef([]);
  const [status, setStatus] = useState("Loading recording...");

  useEffect(() => {
    const term = new Terminal({
      cursorBlink: false,
      fontFamily: "Menlo, Monaco, monospace",
      fontSize: 14
    });
    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(termRef.current);
    fitAddon.fit();

    const load = async () => {
      const response = await apiFetch(`/sessions/${id}/recording`);
      if (!response.ok) {
        setStatus("Recording not available.");
        return;
      }
      const text = await response.text();
      const lines = text.split("\n").filter(Boolean);
      if (!lines.length) {
        setStatus("Recording empty.");
        return;
      }
      const entries = lines.map((line) => JSON.parse(line));
      const start = entries[0].ts;
      entries.forEach((entry) => {
        const delay = Math.max(0, (entry.ts - start) * 1000);
        const timerId = window.setTimeout(() => {
          const data = decodeBase64(entry.data);
          term.write(data);
        }, delay);
        timersRef.current.push(timerId);
      });
      setStatus("Playing");
      const lastEntry = entries[entries.length - 1];
      const endDelay = Math.max(0, (lastEntry.ts - start) * 1000) + 150;
      const endTimer = window.setTimeout(() => {
        setStatus("Playback finished.");
      }, endDelay);
      timersRef.current.push(endTimer);
    };

    load();
    window.addEventListener("resize", () => fitAddon.fit());

    return () => {
      timersRef.current.forEach((timerId) => window.clearTimeout(timerId));
      timersRef.current = [];
      term.dispose();
    };
  }, [id]);

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>Session Replay</h2>
        <button className="secondary" onClick={() => navigate(-1)}>Back</button>
      </div>
      <p>{status}</p>
      <div className="terminal" ref={termRef}></div>
    </div>
  );
}
