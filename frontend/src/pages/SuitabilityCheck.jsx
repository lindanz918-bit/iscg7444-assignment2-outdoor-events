import { useState } from "react";
import { evaluateEvent } from "../api";

const EVENT_TYPES = [
  { value: "sports", label: "Sports" },
  { value: "market", label: "Market" },
  { value: "gathering", label: "Gathering" },
];

const RISK_COLOURS = {
  "Low Risk": "#2e7d32",
  "Moderate Risk": "#ed6c02",
  "High Risk": "#c62828",
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
  const riskColour = (evaluation && RISK_COLOURS[evaluation.risk_level]) || "#333";

  return (
    <section
      style={{
        marginTop: "24px",
        padding: "16px",
        border: "1px solid #ddd",
        borderRadius: "8px",
      }}
    >
      <h2 style={{ marginTop: 0 }}>Weather and Outdoor Suitability</h2>

      <label>
        Event type:{" "}
        <select
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
      </label>{" "}
      <button onClick={handleCheck} disabled={loading}>
        {loading ? "Checking..." : "Check suitability"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {evaluation && (
        <div style={{ marginTop: "16px" }}>
          <p style={{ fontSize: "2rem", margin: "0 0 4px", color: riskColour }}>
            <strong>{evaluation.suitability_score}</strong> / 100
          </p>
          <p style={{ margin: "0 0 8px", color: riskColour }}>
            <strong>{evaluation.risk_level}</strong>
          </p>
          <p>{evaluation.recommendation}</p>
        </div>
      )}

      {weather && (
        <div>
          <h3>Current weather in {weather.location}</h3>
          <ul>
            <li>Conditions: {weather.weather_description}</li>
            <li>
              Temperature: {Math.round(weather.temperature)}°C (feels like{" "}
              {Math.round(weather.feels_like)}°C)
            </li>
            <li>Wind: {weather.wind_speed} m/s</li>
            <li>Humidity: {weather.humidity}%</li>
          </ul>
        </div>
      )}
    </section>
  );
}