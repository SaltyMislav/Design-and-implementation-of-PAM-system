import asyncio
import base64
import json
import os
import threading
import time
from typing import Optional

import jwt
import paramiko
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

GATEWAY_JWT_SECRET = os.getenv("GATEWAY_JWT_SECRET", "dev-gateway-secret")
VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "root")
VAULT_KV_MOUNT = os.getenv("VAULT_KV_MOUNT", "secret")
BACKEND_INTERNAL_URL = os.getenv("BACKEND_INTERNAL_URL", "http://backend:8000")
GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY", "dev-gateway-key")
RECORDINGS_DIR = os.getenv("RECORDINGS_DIR", "/data/recordings")

app = FastAPI(title="PAM Gateway")


def _vault_headers() -> dict:
    return {"X-Vault-Token": VAULT_TOKEN}


def _read_secret(vault_path: str) -> dict:
    url = f"{VAULT_ADDR}/v1/{VAULT_KV_MOUNT}/data/{vault_path}"
    response = requests.get(url, headers=_vault_headers(), timeout=5)
    response.raise_for_status()
    return response.json()["data"]["data"]


def _decode_token(token: str) -> dict:
    return jwt.decode(token, GATEWAY_JWT_SECRET, algorithms=["HS256"])


def _ensure_recording_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _write_json_line(handle, payload: dict) -> None:
    handle.write(json.dumps(payload, separators=(",", ":")) + "\n")
    handle.flush()


async def _notify_session_end(session_id: int) -> None:
    try:
        requests.post(
            f"{BACKEND_INTERNAL_URL}/sessions/{session_id}/end",
            headers={"X-Gateway-Api-Key": GATEWAY_API_KEY},
            timeout=5,
        )
    except Exception:
        pass


@app.websocket("/ws")
async def websocket_proxy(websocket: WebSocket) -> None:
    await websocket.accept()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        claims = _decode_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    session_id = claims.get("session_id")
    vault_path = claims.get("vault_path")
    asset_host = claims.get("asset_host")
    asset_port = int(claims.get("asset_port", 22))
    recording_path = claims.get("recording_path", f"recordings/session-{session_id}.log")

    try:
        secret = _read_secret(vault_path)
    except Exception:
        await websocket.close(code=1011)
        return

    username = secret.get("username")
    password = secret.get("password")
    if not username or not password:
        await websocket.close(code=1011)
        return

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(asset_host, port=asset_port, username=username, password=password)
        channel = client.invoke_shell(term="xterm")
    except Exception:
        await websocket.close(code=1011)
        return

    _ensure_recording_dir(RECORDINGS_DIR)
    recording_file = os.path.join("/data", recording_path)
    cmd_log_file = os.path.join(RECORDINGS_DIR, f"session-{session_id}.cmd.log")
    meta_file = os.path.join(RECORDINGS_DIR, f"session-{session_id}.meta.json")

    with open(meta_file, "w", encoding="utf-8") as meta_handle:
        json.dump(
            {
                "session_id": session_id,
                "asset_host": asset_host,
                "asset_port": asset_port,
                "vault_path": vault_path,
            },
            meta_handle,
        )

    output_handle = open(recording_file, "w", encoding="utf-8")
    cmd_handle = open(cmd_log_file, "w", encoding="utf-8")

    stop_event = threading.Event()
    loop = asyncio.get_running_loop()
    cmd_buffer = ""

    def ssh_reader() -> None:
        while not stop_event.is_set():
            if channel.recv_ready():
                data = channel.recv(4096)
                if not data:
                    break
                payload = {
                    "ts": time.time(),
                    "data": base64.b64encode(data).decode("ascii"),
                }
                _write_json_line(output_handle, payload)
                asyncio.run_coroutine_threadsafe(websocket.send_bytes(data), loop)
            else:
                time.sleep(0.01)
        stop_event.set()

    thread = threading.Thread(target=ssh_reader, daemon=True)
    thread.start()

    try:
        while True:
            message = await websocket.receive()
            data: Optional[bytes] = None
            if message.get("bytes") is not None:
                data = message["bytes"]
            elif message.get("text") is not None:
                data = message["text"].encode()
            if data:
                channel.send(data)
                decoded = data.decode(errors="ignore")
                for char in decoded:
                    if char in ["\n", "\r"]:
                        if cmd_buffer.strip():
                            _write_json_line(
                                cmd_handle,
                                {"ts": time.time(), "line": cmd_buffer.strip()},
                            )
                        cmd_buffer = ""
                    else:
                        cmd_buffer += char
    except WebSocketDisconnect:
        pass
    finally:
        stop_event.set()
        try:
            channel.close()
            client.close()
        except Exception:
            pass
        output_handle.close()
        cmd_handle.close()
        await _notify_session_end(session_id)
        await websocket.close()
