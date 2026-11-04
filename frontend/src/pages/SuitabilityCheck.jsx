import { useState } from "react";
import { evaluateEvent } from "../api";
import "./SuitabilityCheck.css";

const EVENT_TYPES = [
  { value: "sports", label: "Sports" },
  { value: "market", label: "Market" },
  { value: "gathering", label: "Gathering" },
];

const RISK_CLASS_MAP = {
  "Low Risk": "low-risk",
  "Moderate Risk": "moderate-risk",
  "High Risk": "high-risk",
};

export default function SuitabilityCheck({ eventId }) {
  const [eventType, setEventType] = useState("sports");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleCheck() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await evaluateEvent(eventId, eventType);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const evaluation = result && result.evaluation;
  const weather = result && result.weather_data;
  const riskClass = (evaluation && RISK_CLASS_MAP[evaluation.risk_level]) || "";

  return (
    <div className="suitability-check card">
      <h2 className="suitability-title">Weather & Outdoor Suitability</h2>

      <div className="suitability-controls">
        <div className="event-type-selector">
          <label htmlFor="event-type">Event Type</label>
          <select
            id="event-type"
            value={eventType}
            onChange={(e) => {
              setEventType(e.target.value);
              setResult(null);
            }}
          >
            {EVENT_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
        <button 
          className="btn btn-primary check-button"
          onClick={handleCheck} 
          disabled={loading}
        >
          {loading ? "Analysing weather conditions..." : "Check Suitability"}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Analysing weather conditions...</p>
        </div>
      )}

      {evaluation && (
        <div className="suitability-result">
          <div className="score-display">
            <div className="score-number">
              {evaluation.suitability_score}
            </div>
            <div className="score-label">Suitability Score</div>
            <div className="score-max">/ 100</div>
          </div>

          <div className={`risk-badge ${riskClass}`}>
            {evaluation.risk_level}
          </div>

          <div className="recommendation">
            <p>{evaluation.recommendation}</p>
          </div>
        </div>
      )}

      {weather && (
        <div className="weather-info card">
          <h3>Current Weather in {weather.location}</h3>
          <div className="weather-grid">
            <div className="weather-item">
              <span className="weather-icon">🌡️</span>
              <div className="weather-details">
                <span className="weather-label">Temperature</span>
                <span className="weather-value">
                  {Math.round(weather.temperature)}°C 
                  <span className="weather-sub">(feels like {Math.round(weather.feels_like)}°C)</span>
                </span>
              </div>
            </div>
            <div className="weather-item">
              <span className="weather-icon">💨</span>
              <div className="weather-details">
                <span className="weather-label">Wind</span>
                <span className="weather-value">{weather.wind_speed} m/s</span>
              </div>
            </div>
            <div className="weather-item">
              <span className="weather-icon">💧</span>
              <div className="weather-details">
                <span className="weather-label">Humidity</span>
                <span className="weather-value">{weather.humidity}%</span>
              </div>
            </div>
            <div className="weather-item">
              <span className="weather-icon">☁️</span>
              <div className="weather-details">
                <span className="weather-label">Conditions</span>
                <span className="weather-value">{weather.weather_description}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}