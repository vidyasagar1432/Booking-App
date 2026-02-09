import streamlit as st

from booking_app_v2.constants import BOOKING_FIELDS
from booking_app_v2.storage import (
    load_bookings,
    next_booking_id,
    normalize_record,
    save_bookings,
)
from booking_app_v2.ui import render_booking_fields, render_common_fields, render_metrics


def main() -> None:
    st.set_page_config(
        page_title="Travel Booking Organizer v2",
        page_icon="🧭",
        layout="wide",
    )

    st.title("Travel Booking Organizer v2")
    st.caption("Plan, track, and manage bookings in a streamlined workspace.")

    st.sidebar.header("Navigation")
    booking_type = st.sidebar.selectbox(
        "Booking Type",
        list(BOOKING_FIELDS.keys()),
    )
    view = st.sidebar.radio(
        "Workspace",
        ["Overview", "New Booking", "Manage Bookings", "Search & Reports"],
    )

    data = load_bookings()

    if view == "Overview":
        render_overview(data)
    elif view == "New Booking":
        render_new_booking(data, booking_type)
    elif view == "Manage Bookings":
        render_manage(data, booking_type)
    else:
        render_search(data)


def render_overview(data):
    render_metrics(data)

    st.subheader("Recent Bookings")
    if data.empty:
        st.info("No bookings yet. Add your first booking to get started.")
        return

    recent = data.sort_values("booking_id", ascending=False).head(10)
    st.dataframe(recent, use_container_width=True)


def render_new_booking(data, booking_type):
    st.subheader(f"New {booking_type} Booking")

    with st.form("new_booking_form"):
        common_values = render_common_fields()
        booking_values = render_booking_fields(booking_type)
        submitted = st.form_submit_button("Save Booking")

    if submitted:
        booking_id = next_booking_id(data)
        record = {
            "booking_id": booking_id,
            "booking_type": booking_type,
            **common_values,
            **booking_values,
        }
        data = data._append(normalize_record(record, data.columns), ignore_index=True)
        save_bookings(data)
        st.success(f"Booking {booking_id} saved.")


def render_manage(data, booking_type):
    st.subheader("Manage Bookings")

    filtered = data[data["booking_type"] == booking_type]
    if filtered.empty:
        st.info(f"No {booking_type.lower()} bookings available yet.")
        return

    st.dataframe(filtered, use_container_width=True)
    booking_ids = filtered["booking_id"].tolist()
    selected_id = st.selectbox("Select Booking ID", booking_ids)

    selected_row = filtered[filtered["booking_id"] == selected_id].iloc[0].to_dict()

    with st.form("edit_booking_form"):
        st.markdown("#### Edit Booking")
        common_values = render_common_fields(selected_row)
        booking_values = render_booking_fields(booking_type, selected_row)
        update = st.form_submit_button("Update Booking")

    if update:
        updated_record = {
            "booking_id": selected_id,
            "booking_type": booking_type,
            **common_values,
            **booking_values,
        }
        data.loc[data["booking_id"] == selected_id, :] = normalize_record(
            updated_record, data.columns
        )
        save_bookings(data)
        st.success("Booking updated.")

    if st.button("Delete Booking"):
        data = data[data["booking_id"] != selected_id]
        save_bookings(data)
        st.warning("Booking deleted.")


def render_search(data):
    st.subheader("Search & Reports")
    if data.empty:
        st.info("No bookings available to search.")
        return

    with st.expander("Filters", expanded=True):
        name_filter = st.text_input("Client Name Contains")
        status_filter = st.multiselect(
            "Status",
            options=sorted(data["status"].dropna().unique().tolist()),
        )
        type_filter = st.multiselect(
            "Booking Types",
            options=sorted(data["booking_type"].dropna().unique().tolist()),
        )

    filtered = data.copy()
    if name_filter:
        filtered = filtered[filtered["client_name"].str.contains(name_filter, case=False)]
    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]
    if type_filter:
        filtered = filtered[filtered["booking_type"].isin(type_filter)]

    st.dataframe(filtered, use_container_width=True)
    st.download_button(
        "Download CSV",
        data=filtered.to_csv(index=False),
        file_name="booking_report.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
