function WeatherCard({ weather }) {
  return (
    <div>
      <h3>Weather</h3>
      <p>Temperature: {weather.temp}°C</p>
      <p>Rain probability: {weather.rain_probability}%</p>
      <p>Wind speed: {weather.wind_speed} m/s</p>
    </div>
  );
}

export default WeatherCard;