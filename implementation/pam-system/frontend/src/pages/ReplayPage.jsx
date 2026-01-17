import React, { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import { apiFetch } from "../api";
import "xterm/css/xterm.css";

function decodeBase64(data) {
  return Uint8Array.from(atob(data), (c) => c.charCodeAt(0));
}

export default function ReplayPage() {
  const { id } = useParams();
  const termRef = useRef(null);
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
        setTimeout(() => {
          const data = decodeBase64(entry.data);
          term.write(data);
        }, delay);
      });
      setStatus("Playing");
    };

    load();
    window.addEventListener("resize", () => fitAddon.fit());

    return () => term.dispose();
  }, [id]);

  return (
    <div className="card">
      <h2>Session Replay</h2>
      <p>{status}</p>
      <div className="terminal" ref={termRef}></div>
    </div>
  );
}
