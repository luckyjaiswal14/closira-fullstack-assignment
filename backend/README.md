# Closira Backend

## Project Summary

This backend is a lightweight FastAPI service built for the Closira internship assignment. It handles enquiry creation and retrieval, seeds demo data on startup, and exposes the API used by the frontend.

## Features

- Live enquiry listing and detail endpoints
- Automatic seeding of demo enquiries when the database is empty
- Follow-up and escalation actions
- SQLite-backed persistence
- CORS support for browser-based frontend access
- Structured logging for local debugging and review

## Project Structure

- `main.py`: application startup, seed logic, and route definitions
- `schemas.py`: request and response models
- `database.py`: SQLite connection and ORM models
- `tasks.py`: background processing helpers
- `logger.py`: logging configuration

## Run Instructions

```bash
cd backend
python3.12 -m pip install -r requirements.txt
python3.12 -m uvicorn main:app --reload
```

- API base URL: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

## Key Endpoints

- `GET /enquiries`
- `GET /enquiry/{id}`
- `POST /enquiry`
- `POST /enquiry/{id}/follow-up`
- `POST /enquiry/{id}/escalate`

## Notes for Submission

- The backend uses SQLite so it can run locally without external services.
- Demo data is seeded automatically on first startup to make the app immediately usable during review.
- The provided `test.http` file can be used for quick endpoint testing.

## Verification

After startup, confirm the API is available at `http://localhost:8000/enquiries` and the docs page is reachable at `http://localhost:8000/docs`.
