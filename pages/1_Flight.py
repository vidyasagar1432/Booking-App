"""
Flight Booking Management Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.excel_db import ExcelDatabase
from utils.validators import Validators
from config import FLIGHT_FIELDS, CLASS_OPTIONS, STATUS_OPTIONS
import json


st.set_page_config(
    page_title="Flight Bookings",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
db = ExcelDatabase()

st.title("✈️ Flight Bookings")

# Tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View", "➕ Add", "✏️ Edit", "🗑️ Delete"])

with tab1:
    st.subheader("Flight Bookings List")

    # Get all bookings
    df = db.get_bookings("flight")

    if len(df) == 0:
        st.info("No flight bookings found. Add one to get started!")
    else:
        # Statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        stats = db.get_statistics("flight")

        with col1:
            st.metric("Total Bookings", stats.get("total_bookings", 0))
        with col2:
            st.metric("Confirmed", stats.get("confirmed", 0))
        with col3:
            st.metric("Pending", stats.get("pending", 0))
        with col4:
            st.metric("Cancelled", stats.get("cancelled", 0))
        with col5:
            try:
                rev = float(stats.get('total_revenue', 0))
            except (ValueError, TypeError):
                rev = 0.0
            st.metric("Total Revenue", f"${rev:,.2f}")

        st.divider()

        # Search and filter
        col1, col2, col3 = st.columns(3)

        with col1:
            search_field = st.selectbox(
                "Search by", df.columns, key="flight_search_field"
            )

        with col2:
            search_value = st.text_input("Search value", key="flight_search_value")

        if search_value:
            df_filtered = db.search_bookings("flight", search_field, search_value)
        else:
            df_filtered = df

        with col3:
            filter_status = st.multiselect(
                "Filter by Status",
                STATUS_OPTIONS,
                default=STATUS_OPTIONS,
                key="flight_status_filter",
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
                file_name=f"flight_bookings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

with tab2:
    st.subheader("Add New Flight Booking")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Passenger Info**")
        passenger_name = st.text_input("Passenger Name *", key="flight_pname")
        email = st.text_input("Email", key="flight_email")
        phone = st.text_input("Phone Number *", key="flight_phone")
        company_name = st.text_input("Company Name", key="flight_company")

    with col2:
        st.write("**Journey Details**")
        from_airport = st.text_input(
            "From Airport (Code) *", key="flight_from", placeholder="e.g., LAX"
        )
        to_airport = st.text_input(
            "To Airport (Code) *", key="flight_to", placeholder="e.g., JFK"
        )
        departure_date = st.date_input("Departure Date *", key="flight_dep_date")
        departure_time = st.time_input("Departure Time", key="flight_dep_time")
        arrival_date = st.date_input("Arrival Date", key="flight_arr_date")
        arrival_time = st.time_input("Arrival Time", key="flight_arr_time")

    with col3:
        st.write("**Booking Details**")
        airline = st.text_input("Airline *", key="flight_airline")
        flight_number = st.text_input("Flight Number *", key="flight_number")
        seat_number = st.text_input(
            "Seat Number", key="flight_seat", placeholder="e.g., 12A"
        )
        flight_class = st.selectbox("Class", CLASS_OPTIONS, key="flight_class")
        total_cost = st.number_input(
            "Total Cost ($)", min_value=0.0, step=0.01, key="flight_cost"
        )
        status = st.selectbox("Status", STATUS_OPTIONS, index=0, key="flight_status")

    col1, col2 = st.columns(2)

    with col1:
        notes = st.text_area("Notes", height=100, key="flight_notes")
    with col2:
        passengers_text = st.text_area(
            "Passengers (one per line: Name|Company|Phone|Email)",
            height=100,
            key="flight_passengers_text",
        )

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("➕ Add Flight", use_container_width=True):
            # Validate data
            data = {
                "Passenger Name": passenger_name,
                "Email": email,
                "Phone": phone,
                "Airline": airline,
                "Company Name": company_name,
                "Flight Number": flight_number,
                "Departure Date": str(departure_date),
                "From Airport": from_airport,
                "To Airport": to_airport,
            }

            is_valid, error_msg = Validators.validate_flight_data(data)

            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                # Generate booking ID
                booking_id = db.generate_booking_id("flight")

                # Prepare passengers list and complete data
                passengers_list = [
                    l.strip() for l in passengers_text.splitlines() if l.strip()
                ]

                complete_data = {
                    "Booking ID": booking_id,
                    "Passenger Name": passenger_name,
                    "Email": email,
                    "Phone": phone,
                    "Airline": airline,
                    "Company Name": company_name,
                    "Flight Number": flight_number,
                    "Departure Date": departure_date,
                    "Departure Time": str(departure_time),
                    "Arrival Date": arrival_date,
                    "Arrival Time": str(arrival_time),
                    "From Airport": from_airport,
                    "To Airport": to_airport,
                    "Seat Number": seat_number,
                    "Class": flight_class,
                    "Total Cost": total_cost,
                    "Passengers": json.dumps(passengers_list),
                    "Passenger Count": len(passengers_list),
                    "Booking Date": datetime.now().strftime("%Y-%m-%d"),
                    "Status": status,
                    "Notes": notes,
                }

                success, message = db.add_booking("flight", complete_data)
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

with tab3:
    st.subheader("Edit Flight Booking")

    df = db.get_bookings("flight")

    if len(df) == 0:
        st.info("No flight bookings to edit.")
    else:
        # Select booking to edit
        booking_id = st.selectbox(
            "Select Booking ID to Edit", df["Booking ID"].unique(), key="flight_edit_id"
        )

        # Get booking data
        booking = df[df["Booking ID"] == booking_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            passenger_name = st.text_input(
                "Passenger Name",
                value=booking.get("Passenger Name", ""),
                key="flight_edit_pname",
            )
            email = st.text_input(
                "Email", value=booking.get("Email", ""), key="flight_edit_email"
            )
            phone = st.text_input(
                "Phone Number", value=booking.get("Phone", ""), key="flight_edit_phone"
            )
            airline = st.text_input(
                "Airline", value=booking.get("Airline", ""), key="flight_edit_airline"
            )
            company_name = st.text_input(
                "Company Name",
                value=booking.get("Company Name", ""),
                key="flight_edit_company",
            )
            flight_number = st.text_input(
                "Flight Number",
                value=booking.get("Flight Number", ""),
                key="flight_edit_number",
            )
            from_airport = st.text_input(
                "From Airport",
                value=booking.get("From Airport", ""),
                key="flight_edit_from",
            )
            to_airport = st.text_input(
                "To Airport", value=booking.get("To Airport", ""), key="flight_edit_to"
            )

        with col2:
            departure_date = st.date_input(
                "Departure Date",
                value=pd.to_datetime(
                    booking.get("Departure Date", datetime.now())
                ).date(),
                key="flight_edit_dep_date",
            )
            departure_time = st.text_input(
                "Departure Time",
                value=booking.get("Departure Time", ""),
                key="flight_edit_dep_time",
                placeholder="HH:MM",
            )
            arrival_date = st.date_input(
                "Arrival Date",
                value=pd.to_datetime(
                    booking.get("Arrival Date", datetime.now())
                ).date(),
                key="flight_edit_arr_date",
            )
            arrival_time = st.text_input(
                "Arrival Time",
                value=booking.get("Arrival Time", ""),
                key="flight_edit_arr_time",
                placeholder="HH:MM",
            )
            seat_number = st.text_input(
                "Seat Number",
                value=booking.get("Seat Number", ""),
                key="flight_edit_seat",
            )
            flight_class = st.selectbox(
                "Class",
                CLASS_OPTIONS,
                index=(
                    CLASS_OPTIONS.index(booking.get("Class", "Economy"))
                    if booking.get("Class") in CLASS_OPTIONS
                    else 0
                ),
                key="flight_edit_class",
            )
            try:
                total_cost_val = float(booking.get("Total Cost", 0))
            except (ValueError, TypeError):
                total_cost_val = 0.0
            
            total_cost = st.number_input(
                "Total Cost",
                value=total_cost_val,
                min_value=0.0,
                step=0.01,
                key="flight_edit_cost",
            )

        status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=(
                STATUS_OPTIONS.index(booking.get("Status", "Confirmed"))
                if booking.get("Status") in STATUS_OPTIONS
                else 0
            ),
            key="flight_edit_status",
        )
        notes = st.text_area(
            "Notes", value=booking.get("Notes", ""), height=100, key="flight_edit_notes"
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
            key="flight_passengers_edit_text",
        )

        if st.button("✏️ Update Booking", use_container_width=True):
            # Build update payload
            passengers_edit_list = [
                l.strip() for l in passengers_edit_text.splitlines() if l.strip()
            ]

            data = {
                "Passenger Name": passenger_name,
                "Email": email,
                "Phone": phone,
                "Airline": airline,
                "Company Name": company_name,
                "Flight Number": flight_number,
                "From Airport": from_airport,
                "To Airport": to_airport,
                "Departure Date": str(departure_date),
                "Departure Time": departure_time,
                "Arrival Date": str(arrival_date),
                "Arrival Time": arrival_time,
                "Seat Number": seat_number,
                "Class": flight_class,
                "Total Cost": total_cost,
                "Status": status,
                "Notes": notes,
            }
            # include passengers from edit textarea
            data["Passengers"] = json.dumps(passengers_edit_list)
            data["Passenger Count"] = len(passengers_edit_list)

            success, message = db.update_booking("flight", booking_id, data)
            if success:
                st.success(message)
            else:
                st.error(message)

with tab4:
    st.subheader("Delete Flight Booking")

    df = db.get_bookings("flight")

    if len(df) == 0:
        st.info("No flight bookings to delete.")
    else:
        booking_id = st.selectbox(
            "Select Booking ID to Delete",
            df["Booking ID"].unique(),
            key="flight_delete_id",
        )

        booking = df[df["Booking ID"] == booking_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Passenger Name:** {booking.get('Passenger Name', 'N/A')}")
            st.write(f"**Airline:** {booking.get('Airline', 'N/A')}")
            st.write(f"**Flight Number:** {booking.get('Flight Number', 'N/A')}")
            st.write(
                f"**Route:** {booking.get('From Airport', 'N/A')} → {booking.get('To Airport', 'N/A')}"
            )

        with col2:
            st.write(f"**Departure Date:** {booking.get('Departure Date', 'N/A')}")
            st.write(f"**Status:** {booking.get('Status', 'N/A')}")
            try:
                total_cost_val = float(booking.get('Total Cost', 0))
            except (ValueError, TypeError):
                total_cost_val = 0.0
            st.write(f"**Total Cost:** ${total_cost_val:,.2f}")

        st.warning("⚠️ This action cannot be undone!")

        if st.button("🗑️ Delete Booking", use_container_width=True, type="secondary"):
            success, message = db.delete_booking("flight", booking_id)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
