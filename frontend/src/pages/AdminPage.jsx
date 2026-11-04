import { useEffect, useState } from "react";
import { getEvents, createEvent, updateEvent, deleteEvent } from "../api";
import "./AdminPage.css";

const emptyForm = { title: "", description: "", location: "", date: "", time: "", event_type: "" };

function formatDate(date) {
  return date ? date.split("-").reverse().join("/") : "";
}

function formatEventType(type) {
  if (!type) return "General";
  return type.charAt(0).toUpperCase() + type.slice(1);
}

function AdminPage() {
  const [events, setEvents] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadEvents() {
    try {
      const data = await getEvents(1, 100);
      setEvents(data.events);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadEvents();
  }, []);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function resetForm() {
    setForm(emptyForm);
    setEditingId(null);
    setError("");
    setSuccess("");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.title || !form.location || !form.date || !form.event_type) {
      setError("Title, location, date, and event type are required.");
      return;
    }
    setSubmitting(true);
    setError("");
    setSuccess("");
    try {
      if (editingId) {
        await updateEvent(editingId, form);
        setSuccess("Event updated successfully.");
      } else {
        await createEvent(form);
        setSuccess("Event created successfully.");
      }
      resetForm();
      await loadEvents();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleEdit(event) {
    setForm({
      title: event.title,
      description: event.description || "",
      location: event.location,
      date: event.date,
      time: event.time || "",
      event_type: event.event_type || "",
    });
    setEditingId(event.id);
    setError("");
    setSuccess("");
  }

  async function handleDelete(id) {
    if (!window.confirm("Are you sure you want to delete this event?")) return;
    try {
      await deleteEvent(id);
      if (editingId === id) resetForm();
      setError("");
      setSuccess("Event deleted successfully.");
      await loadEvents();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="admin-page">
      <div className="admin-content">
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {success && (
          <div className="success-message">
            <p>{success}</p>
          </div>
        )}

        <div className="form-section card">
          <h2>{editingId ? "Edit Event" : "Create New Event"}</h2>
          <form onSubmit={handleSubmit} className="event-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="title">Title *</label>
                <input
                  id="title"
                  name="title"
                  placeholder="Event title"
                  value={form.title}
                  onChange={handleChange}
                  disabled={submitting}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="event_type">Event Type *</label>
                <select
                  id="event_type"
                  name="event_type"
                  value={form.event_type}
                  onChange={handleChange}
                  disabled={submitting}
                  required
                >
                  <option value="">Select Event Type</option>
                  <option value="sports">Sports</option>
                  <option value="market">Market</option>
                  <option value="gathering">Gathering</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="location">Location *</label>
                <input
                  id="location"
                  name="location"
                  placeholder="Event location"
                  value={form.location}
                  onChange={handleChange}
                  disabled={submitting}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="date">Date *</label>
                <input
                  id="date"
                  name="date"
                  type="date"
                  value={form.date}
                  onChange={handleChange}
                  disabled={submitting}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="time">Time</label>
                <input
                  id="time"
                  name="time"
                  type="time"
                  value={form.time}
                  onChange={handleChange}
                  disabled={submitting}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                placeholder="Event description (optional)"
                value={form.description}
                onChange={handleChange}
                disabled={submitting}
                rows={4}
              />
            </div>

            <div className="form-actions">
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={submitting}
              >
                {submitting ? "Saving..." : editingId ? "Save Changes" : "Create Event"}
              </button>
              {editingId && (
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={resetForm}
                  disabled={submitting}
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>

        <div className="events-list-section">
          <h2>Manage Events</h2>
          
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading events...</p>
            </div>
          ) : events.length === 0 ? (
            <div className="empty-state">
              <p>No events yet. Create your first event above.</p>
            </div>
          ) : (
            <div className="events-list">
              {events.map((event) => (
                <div key={event.id} className="event-item card">
                  <div className="event-item-content">
                    <div className="event-item-header">
                      <div className="event-type-badge">{formatEventType(event.event_type)}</div>
                      <h3 className="event-item-title">{event.title}</h3>
                    </div>
                    <div className="event-item-details">
                      <span className="event-item-detail">
                        📅 {formatDate(event.date)}
                        {event.time && ` · ${event.time}`}
                      </span>
                      <span className="event-item-detail">
                        📍 {event.location}
                      </span>
                    </div>
                    {event.description && (
                      <p className="event-item-description">{event.description}</p>
                    )}
                  </div>
                  <div className="event-item-actions">
                    <button 
                      className="btn btn-secondary"
                      onClick={() => handleEdit(event)}
                      disabled={submitting}
                    >
                      Edit
                    </button>
                    <button 
                      className="btn btn-danger"
                      onClick={() => handleDelete(event.id)}
                      disabled={submitting}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdminPage;