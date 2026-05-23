# Closira Internship Assignment

## Project Summary

This submission is a complete full-stack enquiry management dashboard for Closira. The backend is a FastAPI service with SQLite persistence, and the frontend is an Expo web application that consumes the live API directly.

### What is included

- Live backend endpoints for listing, creating, and viewing enquiries
- Demo data seeded automatically on startup
- Dashboard, leads, escalations, follow-ups, and conversation detail views
- A clean, submission-ready repository with agent-specific files removed

## Repository Structure

- `/backend`: FastAPI backend, SQLite models, logging, and API routes
- `/frontend`: Expo frontend, shared API layer, and screen components

## Run the Project

### 1. Start the backend

```bash
cd backend
python3.12 -m pip install -r requirements.txt
python3.12 -m uvicorn main:app --reload
```

- API base URL: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### 2. Start the frontend

```bash
cd frontend
npm install
npm run web
```

- Web app URL: `http://localhost:8081`

## Final Submission Notes

- The frontend is connected directly to the live backend and no longer depends on static mock data.
- The stale `mock` folder was removed so the repository reflects the final implementation.
- All setup-specific agent notes and prompt artifacts were removed.

Please refer to the READMEs in `/backend` and `/frontend` for module-specific details and usage notes.
