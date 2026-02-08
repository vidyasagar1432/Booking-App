# Booking-App

Streamlit-based travel booking record keeper for managing flights, hotels, trains, and buses.

## Features
- Create, view, edit, and delete bookings by type.
- Dashboard with high-level metrics, status distribution, and revenue trends.
- Filters for quick searching by date, client name, status, and PNR.
- Export filtered data to CSV or Excel.

## Getting Started
### Prerequisites
- Python 3.10+

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the app
```bash
streamlit run app.py
```

The app stores data in `travel_bookings.xlsx` in the project root. Keep the file closed while the app is running.
