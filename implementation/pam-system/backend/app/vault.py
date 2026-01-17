import requests

from app.core.config import settings


def _headers() -> dict:
    return {"X-Vault-Token": settings.VAULT_TOKEN}


def ensure_kv_v2_mount() -> None:
    url = f"{settings.VAULT_ADDR}/v1/sys/mounts/{settings.VAULT_KV_MOUNT}"
    payload = {"type": "kv", "options": {"version": "2"}}
    response = requests.post(url, headers=_headers(), json=payload, timeout=5)
    if response.status_code not in (200, 204, 400):
        response.raise_for_status()


def write_kv2(path: str, data: dict) -> None:
    url = f"{settings.VAULT_ADDR}/v1/{settings.VAULT_KV_MOUNT}/data/{path}"
    response = requests.post(url, headers=_headers(), json={"data": data}, timeout=5)
    response.raise_for_status()


def read_kv2(path: str) -> dict:
    url = f"{settings.VAULT_ADDR}/v1/{settings.VAULT_KV_MOUNT}/data/{path}"
    response = requests.get(url, headers=_headers(), timeout=5)
    response.raise_for_status()
    return response.json()["data"]["data"]
