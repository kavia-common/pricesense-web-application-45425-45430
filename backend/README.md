# PriceSense Backend (FastAPI)

Backend API for product tracking, price history, and alerts.

## Endpoints (aligned with frontend)

- GET /               — Health
- GET /products       — List products
- POST /products      — Create product
- GET /products/{product_id} — Get product
- GET /products/{product_id}/history — Get price history
- GET /alerts         — List alerts
- POST /jobs/fetch-latest — Trigger latest fetch job

OpenAPI: /openapi.json

## Environment

Create a `.env` file and set:

- PORT=3001 (or use your server's default)
- DATABASE_URL=sqlite:///./pricesense.db (example; depends on implementation)
- CORS_ORIGINS=http://localhost:3000

Note: Do not commit .env. The exact variable names depend on implementation; request them from the user if not present.

## Run

- pip install -r requirements.txt
- uvicorn app.main:app --port 3001 --reload

## Notes

- Ensure CORS is configured to allow the frontend origin.
- The frontend uses REACT_APP_API_BASE to point to this service (default http://localhost:3001).
