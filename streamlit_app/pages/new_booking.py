from __future__ import annotations

import streamlit as st

from utils.app_utils import get_db, parse_user_input

STATUS_CHOICES = ["Pending", "Booked", "Confirmed", "Travelled", "Cancelled"]


def _input_for_column(column: str) -> str:
    if column == "Status":
        return st.selectbox(column, STATUS_CHOICES, index=0)
    if column == "Notes":
        return st.text_area(column, placeholder="Optional notes")
    if column == "Booking ID":
        return st.text_input(column, placeholder="Leave blank to auto-generate")
    placeholder = "YYYY-MM-DD" if "Date" in column else "HH:MM:SS" if "Time" in column else ""
    return st.text_input(column, placeholder=placeholder)


def render() -> None:
    st.title("Create New Booking")
    st.caption("Add a new record to any booking sheet in the workbook")

    db = get_db()
    booking_sheets = db.booking_sheets()
    if not booking_sheets:
        st.error("No booking sheets are available in the workbook.")
        return

    selected_sheet = st.selectbox("Booking type", booking_sheets)
    template = db.get_sheet(selected_sheet)
    if template.columns.empty:
        st.error(f"Sheet `{selected_sheet}` has no column schema.")
        return

    st.info(
        "Date fields accept `YYYY-MM-DD` and time fields accept `HH:MM` or `HH:MM:SS`."
    )

    values: dict[str, str] = {}
    with st.form("create_booking_form", clear_on_submit=True):
        columns = list(template.columns)
        left, right = st.columns(2)
        for index, column in enumerate(columns):
            target = left if index % 2 == 0 else right
            with target:
                values[column] = _input_for_column(column)

        submitted = st.form_submit_button("Create Booking", type="primary")

    if not submitted:
        return

    non_id_columns = [column for column in values if column != "Booking ID"]
    if not any(str(values[column]).strip() for column in non_id_columns):
        st.error("At least one field other than Booking ID must be filled.")
        return

    parsed = {column: parse_user_input(column, value) for column, value in values.items()}
    try:
        booking_id = db.append_record(selected_sheet, parsed)
    except Exception as exc:
        st.error(f"Could not create booking: {exc}")
        return

    st.success(f"Booking created successfully. Booking ID: `{booking_id}`")
    st.rerun()

