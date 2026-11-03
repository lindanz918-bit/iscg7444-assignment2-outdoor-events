const API = import.meta.env.VITE_API_URL || "";

export const getToken = () => localStorage.getItem("token");
export const setToken = (token) => localStorage.setItem("token", token);
export const clearToken = () => localStorage.removeItem("token");

async function request(path, options = {}) {
  const token = getToken();
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  let data = null;
  try { data = await res.json(); } catch { /* response was not JSON */ }
  if (!res.ok) {
    throw new Error((data && (data.error || data.msg)) || `Request failed (${res.status})`);
  }
  if (data === null) {
    throw new Error("Unexpected response from the server. Is the backend running?");
  }
  return data;
}

export const login = (email, password) =>
  request("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });

export const getEvents = () => request("/api/events");
export const getEvent = (id) => request(`/api/events/${id}`);
export const createEvent = (event) => request("/api/events", { method: "POST", body: JSON.stringify(event) });
export const updateEvent = (id, event) => request(`/api/events/${id}`, { method: "PUT", body: JSON.stringify(event) });
export const deleteEvent = (id) => request(`/api/events/${id}`, { method: "DELETE" });
export const evaluateEvent = (id, eventType) =>
  request(`/api/evaluation/evaluate/${id}`, { method: "POST", body: JSON.stringify({ event_type: eventType }) });