import WeatherCard from "../components/WeatherCard";
import SuitabilityBadge from "../components/SuitabilityBadge";

function EventDetail({ event, onBack }) {
  return (
    <div>
      <button onClick={onBack}>← Back</button>
      <h1>{event.title}</h1>
      <p>{event.date.split("-").reverse().join("/")} · {event.location}</p>
      <WeatherCard weather={event.weather} />
      <SuitabilityBadge score={event.suitability.score} advice={event.suitability.advice} />
    </div>
  );
}

export default EventDetail;