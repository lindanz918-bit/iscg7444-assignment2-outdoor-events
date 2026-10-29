export const initialEvents = [
  {
    id: 1, title: "Mt Eden Community Market", date: "2026-11-14", location: "Mt Eden, Auckland",
    weather: { temp: 18, rain_probability: 40, wind_speed: 12 },
    suitability: { score: 65, advice: "Moderate Rain Risk" },
  },
  {
    id: 2, title: "Park Football Day", date: "2026-11-15", location: "Western Springs, Auckland",
    weather: { temp: 21, rain_probability: 10, wind_speed: 8 },
    suitability: { score: 90, advice: "Great Weather" },
  },
  {
    id: 3, title: "Beach Clean-up", date: "2026-11-21", location: "Takapuna Beach, Auckland",
    weather: { temp: 15, rain_probability: 80, wind_speed: 25 },
    suitability: { score: 25, advice: "High Rain Risk" },
  },
];


export const defaultWeather = { temp: 18, rain_probability: 30, wind_speed: 10 };
export const defaultSuitability = { score: 70, advice: "Good Weather" };