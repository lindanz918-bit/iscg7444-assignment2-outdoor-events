function EventList({ events, onSelect }) {
  return (
    <div>
      <h1>Community Events</h1>
      {events.map((event) => (
        <div
          key={event.id}
          onClick={() => onSelect(event)}
          style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "12px", marginBottom: "12px", cursor: "pointer" }}
        >
          <h3>{event.title}</h3>
          <p>{event.date.split("-").reverse().join("/")}</p>
          <p>{event.location}</p>
        </div>
      ))}
    </div>
  );
}

export default EventList;