from __future__ import annotations

import streamlit as st

from pages.admin import render as render_admin
from pages.analytics import render as render_analytics
from pages.bus_booking import render as render_bus_booking
from pages.bookings import render as render_bookings
from pages.dashboard import render as render_dashboard
from pages.flight_booking import render as render_flight_booking
from pages.hotel_booking import render as render_hotel_booking
from pages.new_booking import render as render_new_booking
from pages.train_booking import render as render_train_booking
from utils.app_utils import get_db, get_db_path
from utils.auth import render_sidebar_auth


st.set_page_config(
    page_title="Booking Operations Console",
    page_icon=":material/event_available:",
    layout="wide",
)

st.sidebar.title("Booking Console")
render_sidebar_auth()

db_path = get_db_path()
st.sidebar.caption(f"Data file: `{db_path}`")

if not db_path.exists():
    st.error(
        "Booking data file was not found. Place `bookings.xlsx` in `streamlit_app/` "
        "or set `BOOKINGS_FILE` in environment/secrets."
    )
    st.stop()

try:
    db = get_db()
except Exception as exc:  # pragma: no cover - safety branch for UI startup
    st.error(f"Could not load workbook: {exc}")
    st.stop()

st.sidebar.caption(f"Last updated: {db.get_last_updated()}")

navigation = st.navigation(
    {
        "Operations": [
            st.Page(
                render_dashboard,
                title="Dashboard",
                icon=":material/monitoring:",
                url_path="dashboard",
                default=True,
            ),
            st.Page(
                render_analytics,
                title="Analytics",
                icon=":material/analytics:",
                url_path="analytics",
            ),
            st.Page(
                render_bookings,
                title="Bookings",
                icon=":material/table_view:",
                url_path="bookings",
            ),
            st.Page(
                render_new_booking,
                title="New Booking",
                icon=":material/add_circle:",
                url_path="new-booking",
            ),
            st.Page(
                render_flight_booking,
                title="Flight Booking",
                icon=":material/flight:",
                url_path="flight-booking",
            ),
            st.Page(
                render_hotel_booking,
                title="Hotel Booking",
                icon=":material/hotel:",
                url_path="hotel-booking",
            ),
            st.Page(
                render_bus_booking,
                title="Bus Booking",
                icon=":material/directions_bus:",
                url_path="bus-booking",
            ),
            st.Page(
                render_train_booking,
                title="Train Booking",
                icon=":material/train:",
                url_path="train-booking",
            ),
        ],
        "Administration": [
            st.Page(
                render_admin,
                title="Admin",
                icon=":material/admin_panel_settings:",
                url_path="admin",
            )
        ],
    },
    position="sidebar",
)
navigation.run()
