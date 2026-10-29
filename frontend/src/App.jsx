import { useState } from "react";
import { initialEvents } from "./mockData";
import EventList from "./pages/EventList";
import EventDetail from "./pages/EventDetail";
import AdminPage from "./pages/AdminPage";

function App() {
  const [events, setEvents] = useState(initialEvents);
  const [selected, setSelected] = useState(null);
  const [page, setPage] = useState("list");

  return (
    <div style={{ padding: "20px", textAlign: "left" }}>
      <button onClick={() => { setPage("list"); setSelected(null); }}>Events</button>{" "}
      <button onClick={() => { setPage("admin"); setSelected(null); }}>Admin</button>

      {page === "admin" ? (
        <AdminPage events={events} setEvents={setEvents} />
      ) : selected ? (
        <EventDetail event={selected} onBack={() => setSelected(null)} />
      ) : (
        <EventList events={events} onSelect={setSelected} />
      )}
    </div>
  );
}

export default App;