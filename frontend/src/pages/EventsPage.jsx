import { useEffect, useState } from "react";
import { getEvents } from "../api";
import EventDetailPage from "./EventDetailPage";

const EVENTS_PER_PAGE = 10;

function formatDate(d) {
  if (!d) return "";
  const parts = d.split("-");
  if (parts.length !== 3) return d;
  return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedId, setSelectedId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getEvents(page, EVENTS_PER_PAGE)
      .then((data) => {
        setEvents(data.events);
        setTotalPages(data.total_pages);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [page]);

  function goToPage(newPage) {
    setLoading(true);
    setError("");
    setPage(newPage);
  }

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

      {totalPages > 1 && (
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "16px" }}>
          <button onClick={() => goToPage(page - 1)} disabled={page <= 1 || loading}>
            ← Previous
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button onClick={() => goToPage(page + 1)} disabled={page >= totalPages || loading}>
            Next →
          </button>
        </div>
      )}
    </div>
  );
}