# Outdoor Events Application

A web application that helps community event organisers assess weather suitability for outdoor events. The system provides real-time weather data integration, suitability scoring, and risk recommendations based on event type and weather conditions.

## Project Overview

Outdoor community events are frequently disrupted by unpredictable weather conditions. Organisers need reliable tools to evaluate whether weather conditions are suitable for their planned activities. This application addresses this problem by:

- Fetching real-time weather data from OpenWeatherMap
- Calculating suitability scores (0–100) based on temperature, rain probability, and wind speed
- Applying event-specific risk rules (sports, market, gathering)
- Providing clear risk levels and recommendations
- Storing evaluation history for reference

The application is designed as a microservices architecture with separate services for the main backend API and weather analysis, deployed on Render's Free Plan.

## Features

### Core Functionality
- **View Community Events**: Browse all scheduled outdoor events with pagination
- **Admin Authentication**: JWT-based authentication for admin users
- **Event Management**: Create, update, and delete events (admin only)
- **Weather Data Integration**: Current weather and 5-day forecast via OpenWeatherMap API
- **Weather Suitability Evaluation**:
  - Suitability score (0–100) based on weather conditions
  - Risk level classification (Low Risk, Moderate Risk, High Risk)
  - Actionable recommendations for event organisers
  - Event-specific risk rules:
    - **Sports**: Rain probability ≥ 40% triggers additional risk deduction
    - **Market**: Wind speed ≥ 10 m/s triggers additional risk deduction
    - **Gathering**: Temperature < 10°C or > 30°C triggers additional risk deduction
- **Evaluation History**: Stores weather evaluation logs for each event

### Cold-Start Optimisation
- **Backend Automatic Retry**: The Flask backend implements automatic retry logic when calling the Weather Microservice, handling 502, 503, 504 errors and connection timeouts with an 80-second deadline
- **Frontend Wake-Up Request**: The React frontend automatically sends a fire-and-forget GET request to the Microservice health endpoint when the app loads, triggering Render's cold-start process while users browse the website

## System Architecture

```mermaid
graph TD
    A[React Frontend] -->|HTTP| B[Flask Backend]
    B -->|SQLAlchemy| C[PostgreSQL Database]
    B -->|HTTP| D[OpenWeatherMap API]
    B -->|HTTP| E[Weather Microservice]
    
    style A fill:#61dafb
    style B fill:#ffffff
    style C fill:#336791
    style D fill:#f2777a
    style E fill:#ffffff
```

### Component Responsibilities

**React Frontend**
- User interface for viewing and managing events
- Admin login and authentication
- Event creation, editing, and deletion forms
- Weather suitability evaluation display
- Automatic microservice wake-up on page load

**Flask Backend**
- RESTful API for event CRUD operations
- JWT authentication and authorisation
- Weather data fetching from OpenWeatherMap
- Weather suitability evaluation orchestration
- Evaluation log storage in database
- Swagger API documentation at `/docs`

**Weather Microservice**
- Weather suitability score calculation
- Event-specific risk rule application
- Health check endpoint for monitoring
- Standalone analysis endpoint for external use

## Project Structure

```
iscg7444-assignment2-outdoor-events/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory and database configuration
│   │   ├── auth.py              # Authentication endpoints (register, login)
│   │   ├── microservice_client.py # Microservice communication with retry logic
│   │   ├── models.py            # SQLAlchemy models (User, Event, EvaluationLog)
│   │   ├── routes.py            # API endpoints (events, weather, evaluation)
│   │   └── weather.py           # OpenWeatherMap API integration
│   ├── instance/                # SQLite database (local development)
│   ├── Dockerfile               # Backend container definition
│   ├── requirements.txt         # Python dependencies
│   ├── run.py                   # Flask application entry point
│   ├── test_pagination.py       # Pagination tests
│   └── test_routes.py           # API endpoint tests
├── frontend/
│   ├── src/
│   │   ├── pages/               # React page components
│   │   ├── App.jsx              # Main application component
│   │   ├── api.js               # API client functions
│   │   └── main.jsx             # React entry point
│   ├── Dockerfile               # Frontend container definition (multi-stage)
│   ├── package.json             # Node.js dependencies and scripts
│   └── vite.config.js           # Vite configuration
├── microservice/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── routes.py            # Microservice endpoints (health, analyze)
│   │   └── weather_analysis.py  # Suitability score calculation logic
│   ├── Dockerfile               # Microservice container definition
│   ├── requirements.txt         # Python dependencies
│   ├── run.py                   # Flask application entry point
│   ├── test_routes.py           # Microservice endpoint tests
│   └── test_weather_analysis.py # Weather analysis logic tests
├── docker-compose.yml           # Multi-container orchestration
├── .github/
│   └── workflows/
│       └── ci-cd.yml            # GitHub Actions CI/CD pipeline
└── README.md                    # This file
```

## Local Setup (Windows)

### Prerequisites
- Python 3.11 or later
- Node.js 20
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd iscg7444-assignment2-outdoor-events
```

### 2. Backend Setup

Navigate to the backend directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory with the following environment variables:

```env
DATABASE_URL=sqlite:///outdoor_events.db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
OPENWEATHER_API_KEY=your-openweather-api-key-here
MICROSERVICE_URL=http://localhost:5001
```

Run the Flask backend:

```bash
python run.py
```

The backend will start on `http://localhost:5000` and automatically create the SQLite database and a default admin user (username: `admin`, password: `123456`).

### 3. Weather Microservice Setup

Open a new terminal, navigate to the microservice directory, and install dependencies:

```bash
cd microservice
pip install -r requirements.txt
```

Run the microservice:

```bash
python run.py
```

The microservice will start on `http://localhost:5001`.

### 4. Frontend Setup

Open a new terminal, navigate to the frontend directory, and install dependencies:

```bash
cd frontend
npm install
```

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:5000
```

Run the React development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## Docker Compose

To run all services using Docker Compose:

```bash
docker-compose up --build
```

This will:
- Build and start the Weather Microservice on port 5001
- Build and start the Backend on port 5000 (with SQLite database)
- Build and start the Frontend on port 80 (nginx)

The services are connected via a Docker bridge network and communicate using service names (e.g., `microservice` instead of `localhost:5001`).

To stop the services:

```bash
docker-compose down
```

## Environment Variables

### Backend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | Database connection string | `postgresql://user:password@host:port/dbname` or `sqlite:///outdoor_events.db` |
| `SECRET_KEY` | Yes | Flask secret key for session management | `your-secret-key-here` |
| `JWT_SECRET_KEY` | Yes | Secret key for JWT token signing | `your-jwt-secret-key-here` |
| `OPENWEATHER_API_KEY` | Yes | API key for OpenWeatherMap | `your-openweather-api-key-here` |
| `MICROSERVICE_URL` | Yes | URL of the Weather Microservice | `http://localhost:5001` or `https://iscg7444-assignment2-outdoor-events.onrender.com` |

### Frontend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_URL` | Yes | Base URL for Backend API | `http://localhost:5000` or `https://iscg7444-assignment2-outdoor-events-ecgb.onrender.com` |

### Microservice Environment Variables

The microservice does not require additional environment variables beyond the Flask environment configuration.

## API Endpoints

### Authentication

#### Register
- **POST** `/api/auth/register`
- **Body**: `{"username": "string", "email": "string", "password": "string"}`
- **Response**: `201 Created` with user details

#### Login
- **POST** `/api/auth/login`
- **Body**: `{"email": "string", "password": "string"}`
- **Response**: `200 OK` with `access_token` and user details

#### Get Current User
- **GET** `/api/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` with current user details

### Events

#### Get Events (Paginated)
- **GET** `/api/events?page=1&limit=10`
- **Response**: `200 OK` with events list and pagination metadata

#### Get Event by ID
- **GET** `/api/events/<event_id>`
- **Response**: `200 OK` with event details

#### Create Event (Admin Only)
- **POST** `/api/events`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{"title": "string", "location": "string", "date": "string", "description": "string", "time": "string", "event_type": "sports|market|gathering"}`
- **Response**: `201 Created` with event details

#### Update Event (Admin Only)
- **PUT** `/api/events/<event_id>`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: Same as create event (all fields optional)
- **Response**: `200 OK` with updated event details

#### Delete Event (Admin Only)
- **DELETE** `/api/events/<event_id>`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` with success message

### Weather

#### Get Current Weather
- **GET** `/api/weather/current?location=Auckland`
- **Response**: `200 OK` with current weather data

#### Get Weather Forecast
- **GET** `/api/weather/forecast?location=Auckland&days=5`
- **Response**: `200 OK` with 5-day forecast

### Evaluation

#### Evaluate Event Suitability
- **POST** `/api/evaluation/evaluate/<event_id>`
- **Body**: `{"event_type": "sports|market|gathering"}` (optional if event has event_type)
- **Response**: `200 OK` with suitability score, risk level, recommendation, and weather data

#### Get Event Evaluation
- **GET** `/api/evaluation/events/<event_id>`
- **Response**: `200 OK` with latest evaluation for the event

#### Get All Evaluations
- **GET** `/api/evaluation/events`
- **Response**: `200 OK` with all events and their latest evaluations

### Microservice

#### Health Check
- **GET** `/health`
- **Response**: `200 OK` with `{"status": "ok"}`

#### Analyze Weather Suitability
- **POST** `/analyze`
- **Body**: `{"temperature": number, "rain_probability": number, "wind_speed": number, "event_type": "string"}`
- **Response**: `200 OK` with suitability score, risk level, recommendation, and risk factors

**API Documentation**: Interactive Swagger UI is available at `/docs` on the Backend.

## Render Deployment

The application is deployed on Render Free Plan with three separate services:

### Frontend Service
- **URL**: https://iscg7444-assignment2-outdoor-events-yv3a.onrender.com
- **Docker Context**: `./frontend`
- **Port**: 80
- **Environment Variables**: `VITE_API_URL`

### Backend Service
- **URL**: https://iscg7444-assignment2-outdoor-events-ecgb.onrender.com
- **Docker Context**: `./backend`
- **Port**: 5000
- **Environment Variables**: `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`, `OPENWEATHER_API_KEY`, `MICROSERVICE_URL`
- **Database**: PostgreSQL (managed by Render)

### Weather Microservice Service
- **URL**: https://iscg7444-assignment2-outdoor-events.onrender.com
- **Docker Context**: `./microservice`
- **Port**: 5001
- **Environment Variables**: None required

### Deployment Notes
- Each service is deployed independently using its Dockerfile
- PostgreSQL is configured as a managed Render database service
- Services communicate via public URLs (not internal networking)
- Free Plan services spin down after 15 minutes of inactivity

### Cold-Start Behaviour and Improvements

**Render Free Plan Cold-Start**: Services on the Free Plan go to sleep after approximately 15 minutes of inactivity. When a request arrives, Render takes 30–90 seconds to spin the service back up, which can cause timeouts or failures for dependent services.

**Backend Automatic Retry**: The Flask backend (`backend/app/microservice_client.py`) implements automatic retry logic when calling the Weather Microservice:
- Retries on HTTP status codes 502, 503, 504
- Retries on connection timeouts and connection errors
- 80-second deadline with exponential backoff
- Graceful error message if the microservice remains unavailable

**Frontend Wake-Up Request**: The React frontend (`frontend/src/App.jsx`) automatically sends a fire-and-forget GET request to the Microservice `/health` endpoint when the app loads:
- Uses `useEffect` to trigger on component mount
- Sends request with `mode: "no-cors"` to avoid CORS issues
- Does not block page load or user interactions
- Fails silently without displaying errors
- Triggers Render's cold-start process while users browse events

These improvements significantly reduce the likelihood of evaluation failures when users click "Check Suitability" after opening the website.

## Testing

### Backend Tests

Run backend pytest tests:

```bash
cd backend
pytest
```

Run specific test file:

```bash
pytest test_routes.py
```

Run with verbose output:

```bash
pytest -v
```

### Microservice Tests

Run microservice pytest tests:

```bash
cd microservice
pytest
```

### Frontend Tests and Linting

Run frontend linter:

```bash
cd frontend
npm run lint
```

Build frontend for production:

```bash
cd frontend
npm run build
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment. The workflow (`.github/workflows/ci-cd.yml`) includes:

### Build Job
- Checks out code
- Installs Node.js 20 and builds the frontend
- Installs Python 3.11
- Installs backend and microservice dependencies
- Builds Docker images for all three services

### Test Job
- Runs backend pytest tests
- Runs microservice pytest tests
- Runs frontend lint checks

### Deploy Job
- Triggers on push to `main` branch only
- Logs in to Docker Hub
- Builds and pushes Docker images to Docker Hub
- Includes placeholder for deployment commands (not yet implemented)

**Note**: The workflow builds and pushes Docker images to Docker Hub but does not automatically deploy to Render. Deployment to Render is currently manual.

## Team Contributions

- **[Team Member 1]**: Backend API development, database design, authentication
- **[Team Member 2]**: Frontend React development, UI/UX design
- **[Team Member 3]**: Weather Microservice, weather analysis algorithms
- **[Team Member 4]**: Docker configuration, deployment, CI/CD setup
- **[Team Member 5]**: Testing, documentation, cold-start optimisation

## License

This project is developed for ISCG7444 Cloud Application Design & Development at Unitec.
