import streamlit as st

from booking_app.storage import initialize_excel_file
from booking_app.crud import create_booking, view_bookings, edit_booking, delete_booking
from booking_app.views import render_dashboard, search_bookings


def main():
    st.set_page_config(
        page_title="Travel Booking Record Keeper",
        page_icon="✈️",
        layout="wide",
    )

    st.title("Travel Booking Record Keeper")
    st.caption(
        "Manage Flight, Hotel, Train, and Bus bookings using Excel as the database."
    )

    st.sidebar.header("Navigation")
    booking_type = st.sidebar.selectbox(
        "Booking Type",
        ["Flight", "Hotel", "Train", "Bus"],
    )

    action = st.sidebar.radio(
        "Action",
        ["Dashboard", "Create", "View", "Edit", "Delete", "Search"],
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "Tip: Keep the Excel file closed while using this app to avoid file access issues."
    )

    initialize_excel_file()

    if action == "Dashboard":
        render_dashboard()
    elif action == "Create":
        create_booking(booking_type)
    elif action == "View":
        view_bookings(booking_type)
    elif action == "Edit":
        edit_booking(booking_type)
    elif action == "Delete":
        delete_booking(booking_type)
    elif action == "Search":
        search_bookings()
    else:
        st.error("Unknown action.")


if __name__ == "__main__":
    main()
