import { useEffect, useState } from "react";
import { getEvent } from "../api";
import SuitabilityCheck from "./SuitabilityCheck";

function formatDate(d) {
  if (!d) return "";
  const parts = d.split("-");
  if (parts.length !== 3) return d;
  return `${parts[2]}/${parts[1]}/${parts[0]}`;
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
    <div>
      <button onClick={onBack}>← Back to events</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!event && !error && <p>Loading...</p>}
      {event && (
        <div style={{ marginTop: "16px" }}>
          <h1>{event.title}</h1>
          <p>
            <strong>Date:</strong> {formatDate(event.date)}
            {event.time ? ` at ${event.time}` : ""}
          </p>
          <p>
            <strong>Location:</strong> {event.location}
          </p>
          {event.description && <p>{event.description}</p>}
          <SuitabilityCheck eventId={id} />
        </div>
      )}
    </div>
  );
}