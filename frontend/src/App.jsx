import { useState, useEffect } from "react";
import AdminPage from "./pages/AdminPage";
import EventsPage from "./pages/EventsPage";
import LoginPage from "./pages/LoginPage";
import { getToken, clearToken } from "./api";
import "./App.css";

function App() {
  const [view, setView] = useState("events");
  const [loggedIn, setLoggedIn] = useState(!!getToken());

  useEffect(() => {
    const WEATHER_MICROSERVICE_URL = "https://iscg7444-assignment2-outdoor-events.onrender.com";
    fetch(`${WEATHER_MICROSERVICE_URL}/health`, { mode: "no-cors" }).catch(() => {});
  }, []);

  return (
    <div className="app">
      <nav className="nav">
        <div className="nav-container">
          <div className="nav-brand" onClick={() => setView("events")}>
            Community Events
          </div>
          <div className="nav-links">
            <button 
              className={`nav-link ${view === "events" ? "active" : ""}`}
              onClick={() => setView("events")}
            >
              Events
            </button>
            <button 
              className={`nav-link ${view === "admin" ? "active" : ""}`}
              onClick={() => setView("admin")}
            >
              Admin
            </button>
          </div>
        </div>
      </nav>

      <main className="main">
        {view === "events" ? (
          <>
            <section className="hero">
              <h1>Discover Events.</h1>
              <h1>Plan with Confidence.</h1>
              <p>
                Weather-aware outdoor event planning for your community. 
                Get real-time suitability scores and recommendations before you go.
              </p>
            </section>
            <EventsPage />
          </>
        ) : loggedIn ? (
          <div className="admin-container">
            <div className="admin-header">
              <h1>Event Management</h1>
              <button className="btn btn-ghost" onClick={() => { clearToken(); setLoggedIn(false); }}>
                Logout
              </button>
            </div>
            <AdminPage />
          </div>
        ) : (
          <LoginPage onLogin={() => setLoggedIn(true)} />
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <p>ISCG7444 Assignment 2</p>
        </div>
      </footer>
    </div>
  );
}

export default App;