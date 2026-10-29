import { useState } from "react";
import { defaultWeather, defaultSuitability } from "../mockData";

function AdminPage({ events, setEvents }) {
  const emptyForm = { title: "", date: "", location: "" };
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function handleSubmit() {
    if (!form.title || !form.date || !form.location) return;
    if (editingId) {
      setEvents(events.map((ev) => (ev.id === editingId ? { ...ev, ...form } : ev)));
    } else {
      setEvents([
        ...events,
        { id: Date.now(), ...form, weather: defaultWeather, suitability: defaultSuitability },
      ]);
    }
    setForm(emptyForm);
    setEditingId(null);
  }

  function handleEdit(ev) {
    setForm({ title: ev.title, date: ev.date, location: ev.location });
    setEditingId(ev.id);
  }

  function handleDelete(id) {
    setEvents(events.filter((ev) => ev.id !== id));
  }

  return (
    <div>
      <h1>Manage Events</h1>

      <div style={{ marginBottom: "20px", display: "flex", flexWrap: "wrap", gap: "8px" }}>
        <input name="title" placeholder="Title" value={form.title} onChange={handleChange} />{" "}
        <input name="date" type="date" value={form.date} onChange={handleChange} />{" "}
        <input name="location" placeholder="Location" value={form.location} onChange={handleChange} />{" "}
        <button onClick={handleSubmit}>{editingId ? "Save" : "Add"}</button>
      </div>

      {events.map((ev) => (
        <div
          key={ev.id}
          style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "12px", marginBottom: "12px" }}
        >
          <strong>{ev.title}</strong> — {ev.date.split("-").reverse().join("/")} — {ev.location}{" "}
          <button onClick={() => handleEdit(ev)}>Edit</button>{" "}
          <button onClick={() => handleDelete(ev.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}

export default AdminPage;