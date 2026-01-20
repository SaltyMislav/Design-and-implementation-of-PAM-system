import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import "xterm/css/xterm.css";

export default function TerminalPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const termRef = useRef(null);
  const socketRef = useRef(null);
  const [status, setStatus] = useState("Connecting...");

  useEffect(() => {
    const token = sessionStorage.getItem(`session_token_${id}`);
    const wsUrl = sessionStorage.getItem(`session_ws_${id}`);
    if (!token || !wsUrl) {
      setStatus("Missing session token. Start a session from Sessions.");
      return;
    }

    const term = new Terminal({
      cursorBlink: true,
      fontFamily: "Menlo, Monaco, monospace",
      fontSize: 14
    });
    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(termRef.current);
    fitAddon.fit();

    const socket = new WebSocket(`${wsUrl}?token=${token}`);
    socket.binaryType = "arraybuffer";
    socketRef.current = socket;

    socket.onopen = () => {
      setStatus("Connected");
      term.focus();
    };
    socket.onmessage = (event) => {
      if (event.data instanceof ArrayBuffer) {
        term.write(new Uint8Array(event.data));
      } else {
        term.write(event.data);
      }
    };
    socket.onclose = () => setStatus("Disconnected");

    term.onData((data) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(data);
      }
    });

    window.addEventListener("resize", () => fitAddon.fit());

    return () => {
      socket.close();
      term.dispose();
    };
  }, [id]);

  return (
    <div>
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2>Live Session</h2>
          <button
            className="secondary"
            onClick={() => {
              if (socketRef.current) {
                socketRef.current.close();
              }
              setStatus("Disconnected");
              navigate("/sessions");
            }}
          >
            Exit Session
          </button>
        </div>
        <p>{status}</p>
        <div className="terminal" ref={termRef}></div>
      </div>
    </div>
  );
}
