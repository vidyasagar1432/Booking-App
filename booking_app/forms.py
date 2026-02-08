import datetime as dt
from typing import Dict, Optional

import pandas as pd
import streamlit as st

from .constants import CURRENCY_OPTIONS, STATUS_OPTIONS


def parse_date(value) -> Optional[dt.date]:
    if pd.isna(value) or value is None or value == "":
        return None
    if isinstance(value, dt.date):
        return value
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def parse_datetime(value) -> Optional[dt.datetime]:
    if pd.isna(value) or value is None or value == "":
        return None
    if isinstance(value, dt.datetime):
        return value
    try:
        return pd.to_datetime(value)
    except Exception:
        return None


def common_fields(booking_type: str, existing: Optional[pd.Series] = None) -> Dict:
    existing_dict = (
        existing.to_dict() if isinstance(existing, pd.Series) else (existing or {})
    )

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        client_name = st.text_input(
            "Client",
            value=existing_dict.get("client_name", ""),
        )
    with col2:
        client_contact = st.text_input(
            "Contact",
            value=existing_dict.get("client_contact", ""),
            help="Phone or email",
        )
    with col3:
        passengers_default = 1
        try:
            passengers_default = int(existing_dict.get("number_of_passengers", 1) or 1)
        except Exception:
            passengers_default = 1
        number_of_passengers = st.number_input(
            "Pax",
            min_value=1,
            value=passengers_default,
            step=1,
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        booking_date_default = (
            parse_date(existing_dict.get("booking_date")) or dt.date.today()
        )
        booking_date = st.date_input("Booking", value=booking_date_default)
    with col2:
        travel_start_default = (
            parse_date(existing_dict.get("travel_start_date")) or dt.date.today()
        )
        travel_start_date = st.date_input("Start", value=travel_start_default)
    with col3:
        travel_end_default = (
            parse_date(existing_dict.get("travel_end_date")) or travel_start_default
        )
        travel_end_date = st.date_input("End", value=travel_end_default)

    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col1:
        total_amount_default = 0.0
        try:
            total_amount_default = float(existing_dict.get("total_amount", 0) or 0)
        except Exception:
            total_amount_default = 0.0
        total_amount = st.number_input(
            "Amt",
            min_value=0.0,
            value=total_amount_default,
            step=100.0,
        )
    with col2:
        currency_default = existing_dict.get("currency", "INR")
        if currency_default not in CURRENCY_OPTIONS:
            CURRENCY_OPTIONS.append(currency_default)
        currency = st.selectbox(
            "Cur", CURRENCY_OPTIONS, index=CURRENCY_OPTIONS.index(currency_default)
        )
    with col3:
        status_default = existing_dict.get("status", STATUS_OPTIONS[0])
        if status_default not in STATUS_OPTIONS:
            STATUS_OPTIONS.append(status_default)
        status = st.selectbox(
            "Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(status_default)
        )

    vendor = st.text_input(
        "Vendor",
        value=existing_dict.get("vendor", ""),
    )

    st.markdown(
        """
        <style>
        .block-container { padding-top: 8px; padding-bottom: 8px; }
        .metric-card { background-color: #f0f2f6; padding: 8px; border-radius: 6px; margin: 6px 0; }
        .header-title { color: #1f77b4; font-size: 1.8em; font-weight: 600; margin-bottom: 6px; }
        .stButton button { padding: 6px 10px; }
        .stTextInput>div>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div, .stDateInput>div>input, .stTimeInput>div>input { padding: 6px 8px; height: 30px; }
        textarea, .stTextArea>div>textarea { padding: 6px 8px; height: 48px !important; }
        label { font-size: 13px; }
        .stForm div.row-widget.stRadio, .stForm div.row-widget.stSelectbox, .stForm div.row-widget.stTextInput { margin-bottom: 6px; }
        .stMarkdown p, .stCaption { font-size: 13px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    remarks = st.text_area(
        "Remarks",
        value=existing_dict.get("remarks", ""),
        height=48,
    )

    return {
        "booking_type": booking_type,
        "client_name": client_name,
        "client_contact": client_contact,
        "number_of_passengers": number_of_passengers,
        "booking_date": booking_date.isoformat(),
        "travel_start_date": travel_start_date.isoformat(),
        "travel_end_date": travel_end_date.isoformat(),
        "total_amount": total_amount,
        "currency": currency,
        "vendor": vendor,
        "status": status,
        "remarks": remarks,
    }


def flight_fields(existing: Optional[pd.Series] = None) -> Dict:
    existing_dict = (
        existing.to_dict() if isinstance(existing, pd.Series) else (existing or {})
    )

    pnr = st.text_input("PNR", value=existing_dict.get("pnr", ""))
    airline = st.text_input("Airline", value=existing_dict.get("airline", ""))
    flight_number = st.text_input(
        "Flight#", value=existing_dict.get("flight_number", "")
    )
    from_city = st.text_input("From", value=existing_dict.get("from_city", ""))
    to_city = st.text_input("To", value=existing_dict.get("to_city", ""))

    dep_dt_existing = parse_datetime(existing_dict.get("departure_datetime"))
    dep_date_default = dep_dt_existing.date() if dep_dt_existing else dt.date.today()
    dep_time_default = dep_dt_existing.time() if dep_dt_existing else dt.time(9, 0)

    arr_dt_existing = parse_datetime(existing_dict.get("arrival_datetime"))
    arr_date_default = arr_dt_existing.date() if arr_dt_existing else dt.date.today()
    arr_time_default = arr_dt_existing.time() if arr_dt_existing else dt.time(11, 0)

    col1, col2 = st.columns(2)
    with col1:
        dep_date = st.date_input("Departure date", value=dep_date_default)
        dep_time = st.time_input("Departure time", value=dep_time_default)
    with col2:
        arr_date = st.date_input("Arrival date", value=arr_date_default)
        arr_time = st.time_input("Arrival time", value=arr_time_default)

    departure_datetime = dt.datetime.combine(dep_date, dep_time).isoformat(sep=" ")
    arrival_datetime = dt.datetime.combine(arr_date, arr_time).isoformat(sep=" ")

    cabin_class = st.text_input("Cabin", value=existing_dict.get("cabin_class", ""))
    ticket_number = st.text_input(
        "Ticket#", value=existing_dict.get("ticket_number", "")
    )

    return {
        "pnr": pnr,
        "airline": airline,
        "flight_number": flight_number,
        "from_city": from_city,
        "to_city": to_city,
        "departure_datetime": departure_datetime,
        "arrival_datetime": arrival_datetime,
        "cabin_class": cabin_class,
        "ticket_number": ticket_number,
    }


def hotel_fields(existing: Optional[pd.Series] = None) -> Dict:
    existing_dict = (
        existing.to_dict() if isinstance(existing, pd.Series) else (existing or {})
    )

    city = st.text_input("City", value=existing_dict.get("city", ""))
    hotel_name = st.text_input("Hotel", value=existing_dict.get("hotel_name", ""))

    checkin_default = parse_date(existing_dict.get("checkin_date")) or dt.date.today()
    checkout_default = parse_date(existing_dict.get("checkout_date")) or (
        checkin_default + dt.timedelta(days=1)
    )

    col1, col2 = st.columns(2)
    with col1:
        checkin_date = st.date_input("Check-in", value=checkin_default)
    with col2:
        checkout_date = st.date_input("Check-out", value=checkout_default)

    nights_default = (checkout_date - checkin_date).days
    try:
        nights_existing = int(
            existing_dict.get("nights", nights_default) or nights_default
        )
    except Exception:
        nights_existing = nights_default

    nights = st.number_input(
        "Nights",
        min_value=0,
        value=nights_existing,
        step=1,
    )

    room_type = st.text_input("Room", value=existing_dict.get("room_type", ""))
    confirmation_number = st.text_input(
        "Conf#",
        value=existing_dict.get("confirmation_number", ""),
    )

    return {
        "city": city,
        "hotel_name": hotel_name,
        "checkin_date": checkin_date.isoformat(),
        "checkout_date": checkout_date.isoformat(),
        "nights": nights,
        "room_type": room_type,
        "confirmation_number": confirmation_number,
    }


def train_fields(existing: Optional[pd.Series] = None) -> Dict:
    existing_dict = (
        existing.to_dict() if isinstance(existing, pd.Series) else (existing or {})
    )

    pnr = st.text_input("PNR", value=existing_dict.get("pnr", ""))
    train_name = st.text_input("Train", value=existing_dict.get("train_name", ""))
    train_number = st.text_input("Train#", value=existing_dict.get("train_number", ""))
    from_station = st.text_input("From", value=existing_dict.get("from_station", ""))
    to_station = st.text_input("To", value=existing_dict.get("to_station", ""))

    dep_dt_existing = parse_datetime(existing_dict.get("departure_datetime"))
    dep_date_default = dep_dt_existing.date() if dep_dt_existing else dt.date.today()
    dep_time_default = dep_dt_existing.time() if dep_dt_existing else dt.time(9, 0)

    dep_date = st.date_input("Departure date", value=dep_date_default)
    dep_time = st.time_input("Departure time", value=dep_time_default)
    departure_datetime = dt.datetime.combine(dep_date, dep_time).isoformat(sep=" ")

    train_class = st.text_input("Class", value=existing_dict.get("class", ""))
    coach = st.text_input("Coach", value=existing_dict.get("coach", ""))
    seat_or_berth = st.text_input("Seat", value=existing_dict.get("seat_or_berth", ""))

    return {
        "pnr": pnr,
        "train_name": train_name,
        "train_number": train_number,
        "from_station": from_station,
        "to_station": to_station,
        "departure_datetime": departure_datetime,
        "class": train_class,
        "coach": coach,
        "seat_or_berth": seat_or_berth,
    }


def bus_fields(existing: Optional[pd.Series] = None) -> Dict:
    existing_dict = (
        existing.to_dict() if isinstance(existing, pd.Series) else (existing or {})
    )

    pnr = st.text_input("PNR", value=existing_dict.get("pnr", ""))
    operator_name = st.text_input(
        "Operator", value=existing_dict.get("operator_name", "")
    )
    from_city = st.text_input("From", value=existing_dict.get("from_city", ""))
    to_city = st.text_input("To", value=existing_dict.get("to_city", ""))

    dep_dt_existing = parse_datetime(existing_dict.get("departure_datetime"))
    dep_date_default = dep_dt_existing.date() if dep_dt_existing else dt.date.today()
    dep_time_default = dep_dt_existing.time() if dep_dt_existing else dt.time(21, 0)

    arr_dt_existing = parse_datetime(existing_dict.get("arrival_datetime"))
    arr_date_default = arr_dt_existing.date() if arr_dt_existing else dt.date.today()
    arr_time_default = arr_dt_existing.time() if arr_dt_existing else dt.time(6, 0)

    col1, col2 = st.columns(2)
    with col1:
        dep_date = st.date_input("Departure date", value=dep_date_default)
        dep_time = st.time_input("Departure time", value=dep_time_default)
    with col2:
        arr_date = st.date_input("Arrival date", value=arr_date_default)
        arr_time = st.time_input("Arrival time", value=arr_time_default)

    departure_datetime = dt.datetime.combine(dep_date, dep_time).isoformat(sep=" ")
    arrival_datetime = dt.datetime.combine(arr_date, arr_time).isoformat(sep=" ")

    seat_number = st.text_input("Seat", value=existing_dict.get("seat_number", ""))
    bus_type = st.text_input(
        "Bus type",
        value=existing_dict.get("bus_type", ""),
    )

    return {
        "pnr": pnr,
        "operator_name": operator_name,
        "from_city": from_city,
        "to_city": to_city,
        "departure_datetime": departure_datetime,
        "arrival_datetime": arrival_datetime,
        "seat_number": seat_number,
        "bus_type": bus_type,
    }


__all__ = [
    "parse_date",
    "parse_datetime",
    "common_fields",
    "flight_fields",
    "hotel_fields",
    "train_fields",
    "bus_fields",
]
