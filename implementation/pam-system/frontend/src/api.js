const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function getTokens() {
  return {
    access: localStorage.getItem("access_token"),
    refresh: localStorage.getItem("refresh_token")
  };
}

export function setTokens(access, refresh) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

export function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export async function apiFetch(path, options = {}) {
  const headers = options.headers ? { ...options.headers } : {};
  const tokens = getTokens();
  if (tokens.access) {
    headers.Authorization = `Bearer ${tokens.access}`;
  }
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers
  });
  if (response.status === 401 && tokens.refresh) {
    const refreshed = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: tokens.refresh })
    });
    if (refreshed.ok) {
      const data = await refreshed.json();
      setTokens(data.access_token, data.refresh_token);
      return apiFetch(path, options);
    }
    window.dispatchEvent(new Event("auth:unauthorized"));
  } else if (response.status === 401) {
    window.dispatchEvent(new Event("auth:unauthorized"));
  }
  return response;
}

export async function getErrorMessage(response) {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") {
      return data.detail;
    }
    if (Array.isArray(data.detail)) {
      return data.detail.map((item) => item.msg || item).join(", ");
    }
    return JSON.stringify(data);
  } catch (err) {
    return `${response.status} ${response.statusText}`;
  }
}

export default API_URL;
