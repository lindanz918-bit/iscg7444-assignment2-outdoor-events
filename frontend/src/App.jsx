import { useState } from "react";
import AdminPage from "./pages/AdminPage";
import EventsPage from "./pages/EventsPage";
import LoginPage from "./pages/LoginPage";
import { getToken, clearToken } from "./api";

function App() {
  const [view, setView] = useState("events");
  const [loggedIn, setLoggedIn] = useState(!!getToken());

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", textAlign: "left" }}>
      <header
        style={{
          padding: "16px 20px",
          borderBottom: "1px solid #ccc",
          display: "flex",
          alignItems: "center",
          gap: "16px",
        }}
      >
        <h2 style={{ margin: 0 }}>Community Events</h2>
        <button onClick={() => setView("events")}>Events</button>
        <button onClick={() => setView("admin")}>Admin</button>
      </header>

      <main style={{ flex: 1, padding: "20px" }}>
        {view === "events" ? (
          <EventsPage />
        ) : loggedIn ? (
          <>
            <button onClick={() => { clearToken(); setLoggedIn(false); }}>Logout</button>
            <AdminPage />
          </>
        ) : (
          <LoginPage onLogin={() => setLoggedIn(true)} />
        )}
      </main>

      <footer style={{ padding: "12px 20px", borderTop: "1px solid #ccc", color: "#666" }}>
        ISCG7444 Assignment 2
      </footer>
    </div>
  );
}

export default App;