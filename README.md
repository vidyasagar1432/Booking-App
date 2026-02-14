# Booking App Monorepo

This repository now contains **two separate apps**:

- `streamlit_app/` → legacy Streamlit + Excel workflow.
- `fastapi_app/` → FastAPI + SQLModel + SQLite backend with Vue (CDN) frontend.

## Folder structure

```text
Booking-App/
├── streamlit_app/
│   ├── app.py
│   ├── pages/
│   ├── utils/
│   ├── bookings.xlsx
│   └── requirements.txt
├── fastapi_app/
│   ├── main.py
│   ├── static/
│   ├── bookings.db (generated at runtime)
│   └── requirements.txt
├── requirements.txt
└── README.md
```

## Run Streamlit app

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r streamlit_app/requirements.txt
streamlit run streamlit_app/app.py
```

## Run FastAPI app

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r fastapi_app/requirements.txt
uvicorn fastapi_app.main:app --reload
```

Open `http://127.0.0.1:8000` for the FastAPI + Vue app.

## Notes

- FastAPI static and SQLite paths are now resolved relative to `fastapi_app/main.py`, so startup works regardless of current working directory.
- Root `requirements.txt` includes both stacks for convenience, but app-specific requirement files are recommended.
