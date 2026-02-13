# Booking App (Streamlit + Excel)

Streamlit application for managing travel bookings where `bookings.xlsx` is the primary data store.

## Features
- Unified dashboard across Flight, Hotel, Train, and Bus sheets.
- Booking explorer with filters and CSV export.
- New booking form with automatic Booking ID generation.
- Admin-only dashboard for inline edit, delete, and sheet replacement.

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
streamlit run app.py
```

## Optional configuration
- `BOOKINGS_FILE`: path to Excel workbook (default: `bookings.xlsx`)
- `ADMIN_PASSWORD`: admin login password (default fallback: `admin123`)

You can set these in environment variables or Streamlit secrets.

