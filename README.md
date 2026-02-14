# Booking App (FastAPI + SQLModel + SQLite + Vue CDN)

Booking management system with a FastAPI backend and a Vue.js (CDN-only) frontend.

## What is included
- Full CRUD API for bookings with all key fields across Flight, Hotel, Train, and Bus.
- SQLite persistence via SQLModel.
- Admin dashboard with KPI cards (total bookings, revenue, status breakdown).
- Live data refresh via WebSocket broadcasts and periodic auto-refresh fallback.
- Pagination + search + filters on list APIs.
- Consistent JSON response envelope for success and errors.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000`.

## API
- `GET /api/bookings?search=&booking_mode=&status=&page=&page_size=`
- `POST /api/bookings`
- `PATCH /api/bookings/{id}`
- `DELETE /api/bookings/{id}`
- `GET /api/admin/summary`
- `WS /ws` for live updates

## Response format
```json
{
  "success": true,
  "message": "...",
  "data": {},
  "meta": {}
}
```
