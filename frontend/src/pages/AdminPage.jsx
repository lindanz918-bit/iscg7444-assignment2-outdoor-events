import { useEffect, useState } from "react";
import { getEvents, createEvent, updateEvent, deleteEvent } from "../api";

const emptyForm = { title: "", description: "", location: "", date: "", time: "" };

function formatDate(date) {
  return date ? date.split("-").reverse().join("/") : "";
}

function AdminPage() {
  const [events, setEvents] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadEvents() {
    try {
      setEvents(await getEvents());
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
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.title || !form.location || !form.date) {
      setError("Title, location and date are required.");
      return;
    }
    try {
      if (editingId) {
        await updateEvent(editingId, form);
      } else {
        await createEvent(form);
      }
      resetForm();
      setError("");
      await loadEvents();
    } catch (err) {
      setError(err.message);
    }
  }

  function handleEdit(event) {
    setForm({
      title: event.title,
      description: event.description || "",
      location: event.location,
      date: event.date,
      time: event.time || "",
    });
    setEditingId(event.id);
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this event?")) return;
    try {
      await deleteEvent(id);
      if (editingId === id) resetForm();
      setError("");
      await loadEvents();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <h1>Manage Events</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: "8px", maxWidth: "500px", marginBottom: "24px" }}
      >
        <input name="title" placeholder="Title" value={form.title} onChange={handleChange} />
        <textarea name="description" placeholder="Description (optional)" value={form.description} onChange={handleChange} />
        <input name="location" placeholder="Location" value={form.location} onChange={handleChange} />
        <input name="date" type="date" value={form.date} onChange={handleChange} />
        <input name="time" type="time" value={form.time} onChange={handleChange} />
        <div style={{ display: "flex", gap: "8px" }}>
          <button type="submit">{editingId ? "Save" : "Add"}</button>
          {editingId && <button type="button" onClick={resetForm}>Cancel</button>}
        </div>
      </form>

      {loading ? (
        <p>Loading...</p>
      ) : events.length === 0 ? (
        <p>No events yet.</p>
      ) : (
        events.map((event) => (
          <div
            key={event.id}
            style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "12px", marginBottom: "12px" }}
          >
            <strong>{event.title}</strong>
            <p style={{ margin: "4px 0" }}>
              {formatDate(event.date)}
              {event.time ? ` · ${event.time}` : ""} · {event.location}
            </p>
            {event.description && <p style={{ margin: "4px 0" }}>{event.description}</p>}
            <button onClick={() => handleEdit(event)}>Edit</button>{" "}
            <button onClick={() => handleDelete(event.id)}>Delete</button>
          </div>
        ))
      )}
    </div>
  );
}

export default AdminPage;