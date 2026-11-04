import { useEffect, useState } from "react";
import { getEvent } from "../api";
import SuitabilityCheck from "./SuitabilityCheck";
import "./EventDetailPage.css";

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

export default function EventDetailPage({ id, onBack }) {
  const [event, setEvent] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getEvent(id)
      .then((data) => setEvent(data.event || data))
      .catch((err) => setError(err.message));
  }, [id]);

  return (
    <div className="event-detail-page">
      <div className="event-detail-container">
        <button className="btn btn-ghost back-button" onClick={onBack}>
          ← Back to Events
        </button>

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {!event && !error && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading event details...</p>
          </div>
        )}

        {event && (
          <div className="event-detail-content">
            <div className="event-header">
              <div className="event-type-badge">{formatEventType(event.event_type)}</div>
              <h1 className="event-title">{event.title}</h1>
            </div>

            <div className="event-info-grid">
              <div className="info-card card">
                <div className="info-card-icon">📅</div>
                <div className="info-card-content">
                  <span className="info-label">Date</span>
                  <span className="info-value">
                    {formatDate(event.date)}
                    {event.time && ` at ${event.time}`}
                  </span>
                </div>
              </div>

              <div className="info-card card">
                <div className="info-card-icon">📍</div>
                <div className="info-card-content">
                  <span className="info-label">Location</span>
                  <span className="info-value">{event.location}</span>
                </div>
              </div>
            </div>

            {event.description && (
              <div className="event-description card">
                <h3>About This Event</h3>
                <p>{event.description}</p>
              </div>
            )}

            <SuitabilityCheck eventId={id} />
          </div>
        )}
      </div>
    </div>
  );
}