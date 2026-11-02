import { useEffect, useState } from "react";
import { getEvents } from "../api";
import EventDetailPage from "./EventDetailPage";

function formatDate(d) {
  if (!d) return "";
  const parts = d.split("-");
  if (parts.length !== 3) return d;
  return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getEvents()
      .then((data) => setEvents(Array.isArray(data) ? data : data.events || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (selectedId !== null) {
    return <EventDetailPage id={selectedId} onBack={() => setSelectedId(null)} />;
  }

  return (
    <div>
      <h1>Upcoming Events</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {loading && <p>Loading...</p>}
      {!loading && !error && events.length === 0 && <p>No events yet.</p>}
      <div style={{ display: "grid", gap: "12px" }}>
        {events.map((ev) => (
          <div
            key={ev.id}
            style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "16px" }}
          >
            <h3 style={{ margin: "0 0 6px" }}>{ev.title}</h3>
            <p style={{ margin: "0 0 10px", color: "#666" }}>
              {formatDate(ev.date)}
              {ev.time ? ` ${ev.time}` : ""} · {ev.location}
            </p>
            <button onClick={() => setSelectedId(ev.id)}>View details</button>
          </div>
        ))}
      </div>
    </div>
  );
}