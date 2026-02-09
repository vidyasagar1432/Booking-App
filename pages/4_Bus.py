"""
Bus Booking Management Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.excel_db import ExcelDatabase
from utils.validators import Validators
from config import BUS_FIELDS, STATUS_OPTIONS
import json


st.set_page_config(
    page_title="Bus Bookings",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
db = ExcelDatabase()

st.title("🚌 Bus Bookings")

# Tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View", "➕ Add", "✏️ Edit", "🗑️ Delete"])

with tab1:
    st.subheader("Bus Bookings List")

    # Get all bookings
    df = db.get_bookings("bus")

    if len(df) == 0:
        st.info("No bus bookings found. Add one to get started!")
    else:
        # Statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        stats = db.get_statistics("bus")

        with col1:
            st.metric("Total Bookings", stats.get("total_bookings", 0))
        with col2:
            st.metric("Confirmed", stats.get("confirmed", 0))
        with col3:
            st.metric("Pending", stats.get("pending", 0))
        with col4:
            st.metric("Cancelled", stats.get("cancelled", 0))
        with col5:
            st.metric("Total Revenue", f"${stats.get('total_revenue', 0):,.2f}")

        st.divider()

        # Search and filter
        col1, col2, col3 = st.columns(3)

        with col1:
            search_field = st.selectbox("Search by", df.columns, key="bus_search_field")

        with col2:
            search_value = st.text_input("Search value", key="bus_search_value")

        if search_value:
            df_filtered = db.search_bookings("bus", search_field, search_value)
        else:
            df_filtered = df

        with col3:
            filter_status = st.multiselect(
                "Filter by Status",
                STATUS_OPTIONS,
                default=STATUS_OPTIONS,
                key="bus_status_filter",
            )
            if filter_status:
                df_filtered = df_filtered[df_filtered["Status"].isin(filter_status)]

        st.divider()

        # Display table
        st.dataframe(
            df_filtered,
            use_container_width=True,
            height=400,
        )

        # Export button
        if len(df_filtered) > 0:
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"bus_bookings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

with tab2:
    st.subheader("Add New Bus Booking")

    col1, col2 = st.columns(2)

    with col1:
        passenger_name = st.text_input("Passenger Name *", key="bus_pname")
        email = st.text_input("Email", key="bus_email")
        phone = st.text_input("Phone Number *", key="bus_phone")
        bus_company = st.text_input("Bus Company *", key="bus_company")
        company_name = st.text_input("Company Name", key="bus_company_name")
        bus_number = st.text_input("Bus Number", key="bus_number")
        from_city = st.text_input("From City *", key="bus_from")
        to_city = st.text_input("To City *", key="bus_to")

    with col2:
        departure_date = st.date_input("Departure Date *", key="bus_dep_date")
        departure_time = st.time_input("Departure Time", key="bus_dep_time")
        arrival_date = st.date_input("Arrival Date", key="bus_arr_date")
        arrival_time = st.time_input("Arrival Time", key="bus_arr_time")
        seat_number = st.text_input(
            "Seat Number", key="bus_seat", placeholder="e.g., A12"
        )
        total_cost = st.number_input(
            "Total Cost ($)", min_value=0.0, step=0.01, key="bus_cost"
        )

    notes = st.text_area("Notes", height=100, key="bus_notes")
    passengers_text = st.text_area(
        "Passengers (one per line: Name|Company|Phone|Email)",
        height=120,
        key="bus_passengers_text",
    )

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("➕ Add Bus Booking", use_container_width=True):
            # Validate data
            data = {
                "Passenger Name": passenger_name,
                "Email": email,
                "Phone": phone,
                "Bus Company": bus_company,
                "Company Name": company_name,
                "Departure Date": str(departure_date),
                "From City": from_city,
                "To City": to_city,
            }

            is_valid, error_msg = Validators.validate_bus_data(data)

            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                # Generate booking ID
                booking_id = db.generate_booking_id("bus")

                # Prepare complete data
                passengers_list = [
                    l.strip() for l in passengers_text.splitlines() if l.strip()
                ]

                complete_data = {
                    "Booking ID": booking_id,
                    "Passenger Name": passenger_name,
                    "Email": email,
                    "Phone": phone,
                    "Bus Company": bus_company,
                    "Company Name": company_name,
                    "Bus Number": bus_number,
                    "Departure Date": str(departure_date),
                    "Departure Time": str(departure_time),
                    "Arrival Date": str(arrival_date),
                    "Arrival Time": str(arrival_time),
                    "From City": from_city,
                    "To City": to_city,
                    "Seat Number": seat_number,
                    "Total Cost": total_cost,
                    "Booking Date": datetime.now().strftime("%Y-%m-%d"),
                    "Passengers": json.dumps(passengers_list),
                    "Passenger Count": len(passengers_list),
                    "Status": "Confirmed",
                    "Notes": notes,
                }

                success, message = db.add_booking("bus", complete_data)
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

with tab3:
    st.subheader("Edit Bus Booking")

    df = db.get_bookings("bus")

    if len(df) == 0:
        st.info("No bus bookings to edit.")
    else:
        # Select booking to edit
        booking_id = st.selectbox(
            "Select Booking ID to Edit", df["Booking ID"].unique(), key="bus_edit_id"
        )

        # Get booking data
        booking = df[df["Booking ID"] == booking_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            passenger_name = st.text_input(
                "Passenger Name",
                value=booking.get("Passenger Name", ""),
                key="bus_edit_pname",
            )
            email = st.text_input(
                "Email", value=booking.get("Email", ""), key="bus_edit_email"
            )
            phone = st.text_input(
                "Phone Number", value=booking.get("Phone", ""), key="bus_edit_phone"
            )
            bus_company = st.text_input(
                "Bus Company",
                value=booking.get("Bus Company", ""),
                key="bus_edit_company",
            )
            company_name = st.text_input(
                "Company Name",
                value=booking.get("Company Name", ""),
                key="bus_edit_company_name",
            )
            bus_number = st.text_input(
                "Bus Number", value=booking.get("Bus Number", ""), key="bus_edit_number"
            )
            from_city = st.text_input(
                "From City", value=booking.get("From City", ""), key="bus_edit_from"
            )
            to_city = st.text_input(
                "To City", value=booking.get("To City", ""), key="bus_edit_to"
            )

        with col2:
            departure_date = st.date_input(
                "Departure Date",
                value=pd.to_datetime(
                    booking.get("Departure Date", datetime.now())
                ).date(),
                key="bus_edit_dep_date",
            )
            departure_time = st.text_input(
                "Departure Time",
                value=booking.get("Departure Time", ""),
                key="bus_edit_dep_time",
                placeholder="HH:MM",
            )
            arrival_date = st.date_input(
                "Arrival Date",
                value=pd.to_datetime(
                    booking.get("Arrival Date", datetime.now())
                ).date(),
                key="bus_edit_arr_date",
            )
            arrival_time = st.text_input(
                "Arrival Time",
                value=booking.get("Arrival Time", ""),
                key="bus_edit_arr_time",
                placeholder="HH:MM",
            )
            seat_number = st.text_input(
                "Seat Number", value=booking.get("Seat Number", ""), key="bus_edit_seat"
            )
            total_cost = st.number_input(
                "Total Cost",
                value=float(booking.get("Total Cost", 0)),
                min_value=0.0,
                step=0.01,
                key="bus_edit_cost",
            )

        status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=(
                STATUS_OPTIONS.index(booking.get("Status", "Confirmed"))
                if booking.get("Status") in STATUS_OPTIONS
                else 0
            ),
            key="bus_edit_status",
        )
        notes = st.text_area(
            "Notes", value=booking.get("Notes", ""), height=100, key="bus_edit_notes"
        )

        if st.button("✏️ Update Booking", use_container_width=True):
            data = {
                "Passenger Name": passenger_name,
                "Email": email,
                "Phone": phone,
                "Bus Company": bus_company,
                "Company Name": company_name,
                "Bus Number": bus_number,
                "Departure Date": str(departure_date),
                "Departure Time": departure_time,
                "Arrival Date": str(arrival_date),
                "Arrival Time": arrival_time,
                "From City": from_city,
                "To City": to_city,
                "Seat Number": seat_number,
                "Total Cost": total_cost,
                "Status": status,
                "Notes": notes,
            }

            # For bus updates, derive passenger count from stored passengers if not explicitly edited
            try:
                existing_passengers = booking.get("Passengers", "")
                if existing_passengers:
                    parsed = (
                        json.loads(existing_passengers)
                        if isinstance(existing_passengers, str)
                        else list(existing_passengers)
                    )
                else:
                    parsed = []
            except Exception:
                parsed = []

            data["Passengers"] = json.dumps(parsed)
            data["Passenger Count"] = len(parsed)

            success, message = db.update_booking("bus", booking_id, data)
            if success:
                st.success(message)
            else:
                st.error(message)

with tab4:
    st.subheader("Delete Bus Booking")

    df = db.get_bookings("bus")

    if len(df) == 0:
        st.info("No bus bookings to delete.")
    else:
        booking_id = st.selectbox(
            "Select Booking ID to Delete",
            df["Booking ID"].unique(),
            key="bus_delete_id",
        )

        booking = df[df["Booking ID"] == booking_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Passenger Name:** {booking.get('Passenger Name', 'N/A')}")
            st.write(f"**Bus Company:** {booking.get('Bus Company', 'N/A')}")
            st.write(f"**Bus Number:** {booking.get('Bus Number', 'N/A')}")

        with col2:
            st.write(
                f"**Route:** {booking.get('From City', 'N/A')} → {booking.get('To City', 'N/A')}"
            )
            # Prefill passengers text area from stored JSON (if available)
            existing_passengers = booking.get("Passengers", "")
            try:
                if existing_passengers:
                    if isinstance(existing_passengers, str):
                        parsed = json.loads(existing_passengers)
                    else:
                        parsed = list(existing_passengers)
                    passengers_edit_text = "\n".join(parsed)
                else:
                    passengers_edit_text = ""
            except Exception:
                passengers_edit_text = str(existing_passengers)

            passengers_edit_text = st.text_area(
                "Passengers (one per line: Name|Company|Phone|Email)",
                value=passengers_edit_text,
                height=120,
                key="bus_passengers_edit_text",
            )
            st.write(f"**Departure Date:** {booking.get('Departure Date', 'N/A')}")
            st.write(f"**Status:** {booking.get('Status', 'N/A')}")
            st.write(f"**Total Cost:** ${booking.get('Total Cost', 0):,.2f}")

        st.warning("⚠️ This action cannot be undone!")

        if st.button("🗑️ Delete Booking", use_container_width=True, type="secondary"):
            success, message = db.delete_booking("bus", booking_id)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
