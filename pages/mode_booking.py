from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.app_utils import (
    format_currency,
    get_db,
    infer_trip_date_column,
    parse_user_input,
    to_display_frame,
)

STATUS_CHOICES = ["Pending", "Booked", "Confirmed", "Travelled", "Cancelled"]


def _input_for_column(column: str, key_prefix: str) -> str:
    if column == "Status":
        return st.selectbox(column, STATUS_CHOICES, index=0, key=f"{key_prefix}_{column}")
    if column == "Notes":
        return st.text_area(column, placeholder="Optional notes", key=f"{key_prefix}_{column}")
    if column == "Booking ID":
        return st.text_input(
            column,
            placeholder="Leave blank to auto-generate",
            key=f"{key_prefix}_{column}",
        )

    placeholder = ""
    if "Date" in column:
        placeholder = "YYYY-MM-DD"
    elif "Time" in column:
        placeholder = "HH:MM:SS"
    return st.text_input(column, placeholder=placeholder, key=f"{key_prefix}_{column}")


def render_mode_booking(mode: str) -> None:
    st.title(f"{mode} Booking")
    st.caption(f"View and create {mode.lower()} bookings in the `{mode}` sheet")

    db = get_db()
    if mode not in db.booking_sheets():
        st.error(f"`{mode}` sheet is not available in the workbook.")
        return

    mode_df = db.get_sheet(mode)

    total_bookings = len(mode_df)
    total_cost = float(pd.to_numeric(mode_df.get("Total Cost"), errors="coerce").fillna(0).sum())
    upcoming = 0
    trip_date_col = infer_trip_date_column(mode_df)
    if trip_date_col:
        trip_dates = pd.to_datetime(mode_df[trip_date_col], errors="coerce")
        upcoming = int((trip_dates >= pd.Timestamp.today().normalize()).sum())

    m1, m2, m3 = st.columns(3)
    m1.metric(f"{mode} Bookings", f"{total_bookings:,}")
    m2.metric(f"{mode} Spend", format_currency(total_cost))
    m3.metric(f"Upcoming {mode}", f"{upcoming:,}")

    st.subheader(f"Existing {mode} Records")
    if mode_df.empty:
        st.info(f"No {mode.lower()} bookings yet.")
    else:
        st.dataframe(to_display_frame(mode_df), width="stretch", hide_index=True)

    st.subheader(f"Add {mode} Booking")
    st.info("Date fields accept `YYYY-MM-DD`; time fields accept `HH:MM` or `HH:MM:SS`.")

    values: dict[str, str] = {}
    with st.form(f"{mode.lower()}_booking_form", clear_on_submit=True):
        left, right = st.columns(2)
        for idx, column in enumerate(mode_df.columns):
            target = left if idx % 2 == 0 else right
            with target:
                values[column] = _input_for_column(column, key_prefix=mode.lower())

        submitted = st.form_submit_button(f"Create {mode} Booking", type="primary")

    if not submitted:
        return

    non_id_columns = [column for column in values if column != "Booking ID"]
    if not any(str(values[column]).strip() for column in non_id_columns):
        st.error("At least one field other than Booking ID must be filled.")
        return

    parsed = {column: parse_user_input(column, value) for column, value in values.items()}
    try:
        booking_id = db.append_record(mode, parsed)
    except Exception as exc:
        st.error(f"Could not create {mode.lower()} booking: {exc}")
        return

    st.success(f"{mode} booking created successfully. Booking ID: `{booking_id}`")
    st.rerun()

