from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.app_utils import get_db, sanitize_editor_frame, to_display_frame
from utils.auth import require_admin


def _read_uploaded_file(uploaded_file) -> pd.DataFrame:
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file, engine="openpyxl")


def render() -> None:
    st.title("Admin Dashboard")
    require_admin()

    db = get_db()
    sheets = db.booking_sheets()
    selected_sheet = st.selectbox("Manage sheet", sheets)
    frame = db.get_sheet(selected_sheet)

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{len(frame):,}")
    c2.metric("Columns", f"{len(frame.columns):,}")
    c3.metric("Last Updated", db.get_last_updated())

    if "Booking ID" in frame.columns:
        ids = frame["Booking ID"].astype(str).str.strip()
        duplicate_ids = int(ids[ids.ne("")].duplicated().sum())
        missing_ids = int(ids.eq("").sum())
        d1, d2 = st.columns(2)
        d1.metric("Duplicate Booking IDs", f"{duplicate_ids:,}")
        d2.metric("Missing Booking IDs", f"{missing_ids:,}")

    st.subheader("Inline Editor")
    edited = st.data_editor(
        to_display_frame(frame),
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        key=f"editor_{selected_sheet}",
    )

    with open(db.file_path, "rb") as source:
        workbook_bytes = source.read()

    actions = st.columns(3)
    if actions[0].button("Save Sheet Changes", type="primary", width="stretch"):
        try:
            cleaned = sanitize_editor_frame(edited, list(frame.columns))
            db.save_sheet(selected_sheet, cleaned)
            st.success("Sheet updated successfully.")
            st.rerun()
        except Exception as exc:
            st.error(f"Save failed: {exc}")

    if actions[1].button("Reload", width="stretch"):
        st.rerun()

    actions[2].download_button(
        "Download Workbook",
        data=workbook_bytes,
        file_name="bookings.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

    st.subheader("Delete Booking")
    if "Booking ID" not in frame.columns:
        st.info("This sheet does not contain a Booking ID column.")
    else:
        booking_ids = sorted(
            booking_id
            for booking_id in frame["Booking ID"].astype(str).str.strip().tolist()
            if booking_id
        )
        selected_id = st.selectbox(
            "Select Booking ID",
            options=[""] + booking_ids,
            format_func=lambda value: value if value else "Choose Booking ID",
        )
        if st.button("Delete Selected Booking", disabled=not selected_id):
            deleted = db.delete_record(selected_sheet, selected_id)
            if deleted:
                st.success(f"Deleted booking `{selected_id}`")
                st.rerun()
            else:
                st.error("Booking ID was not found.")

    st.subheader("Replace Sheet from File")
    st.caption("Upload CSV or XLSX. Uploaded data will be aligned to this sheet's columns.")
    upload = st.file_uploader("Upload replacement data", type=["csv", "xlsx"])
    if upload is not None and st.button("Replace Sheet", type="secondary"):
        try:
            incoming = _read_uploaded_file(upload)
            replacement = sanitize_editor_frame(incoming, list(frame.columns))
            db.save_sheet(selected_sheet, replacement)
            st.success(f"Replaced `{selected_sheet}` with uploaded data.")
            st.rerun()
        except Exception as exc:
            st.error(f"Replace failed: {exc}")
