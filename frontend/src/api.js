   const API = import.meta.env.VITE_API_URL || "";

   async function request(path, options) {
     const res = await fetch(`${API}${path}`, {
       headers: { "Content-Type": "application/json" },
       ...options,
     });
     let data = null;
     try {
       data = await res.json();
     } catch {
       // response was not JSON
     }
          if (!res.ok) {
       throw new Error((data && data.error) || `Request failed (${res.status})`);
     }
     if (data === null) {
       throw new Error("Unexpected response from the server. Is the backend running?");
     }
     return data;
   }

   export const getEvents = () => request("/api/events");

   export const createEvent = (event) =>
     request("/api/events", { method: "POST", body: JSON.stringify(event) });

   export const updateEvent = (id, event) =>
     request(`/api/events/${id}`, { method: "PUT", body: JSON.stringify(event) });

   export const deleteEvent = (id) =>
     request(`/api/events/${id}`, { method: "DELETE" });