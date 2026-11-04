import { useEffect, useState } from "react";
import { getEvents } from "../api";
import EventDetailPage from "./EventDetailPage";
import "./EventsPage.css";

const EVENTS_PER_PAGE = 10;

function formatDate(d) {
  if (!d) return "";
  const parts = d.split("-");
  if (parts.length !== 3) return d;
  return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

function formatEventType(type) {
  if (!type) return "General";
  return type.charAt(0).toUpperCase() + type.slice(1);
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
    <div className="events-page">
      <div className="events-container">
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
        
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading events...</p>
          </div>
        ) : !error && events.length === 0 ? (
          <div className="empty-state">
            <p>No events yet.</p>
          </div>
        ) : (
          <>
            <div className="events-grid">
              {events.map((ev) => (
                <div key={ev.id} className="event-card card">
                  <div className="event-card-content">
                    <div className="event-type-badge">{formatEventType(ev.event_type)}</div>
                    <h3 className="event-title">{ev.title}</h3>
                    <div className="event-details">
                      <div className="event-detail-item">
                        <span className="detail-icon">📅</span>
                        <span>{formatDate(ev.date)}</span>
                        {ev.time && <span> · {ev.time}</span>}
                      </div>
                      <div className="event-detail-item">
                        <span className="detail-icon">📍</span>
                        <span>{ev.location}</span>
                      </div>
                    </div>
                  </div>
                  <button 
                    className="btn btn-primary event-card-button"
                    onClick={() => setSelectedId(ev.id)}
                  >
                    View Details
                  </button>
                </div>
              ))}
            </div>

            {totalPages > 1 && (
              <div className="pagination">
                <button 
                  className="btn btn-secondary pagination-button"
                  onClick={() => goToPage(page - 1)} 
                  disabled={page <= 1 || loading}
                >
                  ← Previous
                </button>
                <span className="pagination-info">
                  Page {page} of {totalPages}
                </span>
                <button 
                  className="btn btn-secondary pagination-button"
                  onClick={() => goToPage(page + 1)} 
                  disabled={page >= totalPages || loading}
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}