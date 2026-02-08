import os
import io
import datetime as dt
from typing import Dict, Optional

import pandas as pd
import streamlit as st

# ==============================
# Constants & Configuration
# ==============================

EXCEL_FILE = "travel_bookings.xlsx"

COMMON_COLUMNS = [
    "id",
    "booking_type",
    "client_name",
    "client_contact",
    "booking_date",
    "travel_start_date",
    "travel_end_date",
    "total_amount",
    "currency",
    "vendor",
    "status",
    "remarks",
]

FLIGHT_EXTRA = [
    "pnr",
    "airline",
    "flight_number",
    "from_city",
    "to_city",
    "departure_datetime",
    "arrival_datetime",
    "cabin_class",
    "ticket_number",
]

HOTEL_EXTRA = [
    "city",
    "hotel_name",
    "checkin_date",
    "checkout_date",
    "nights",
    "room_type",
    "confirmation_number",
]

TRAIN_EXTRA = [
    "pnr",
    "train_name",
    "train_number",
    "from_station",
    "to_station",
    "departure_datetime",
    "class",
    "coach",
    "seat_or_berth",
]

BUS_EXTRA = [
    "pnr",
    "operator_name",
    "from_city",
    "to_city",
    "departure_datetime",
    "arrival_datetime",
    "seat_number",
    "bus_type",
]

SHEETS_CONFIG: Dict[str, Dict[str, list]] = {
    "Flight": {"columns": COMMON_COLUMNS + FLIGHT_EXTRA},
    "Hotel": {"columns": COMMON_COLUMNS + HOTEL_EXTRA},
    "Train": {"columns": COMMON_COLUMNS + TRAIN_EXTRA},
    "Bus": {"columns": COMMON_COLUMNS + BUS_EXTRA},
}

STATUS_OPTIONS = ["Confirmed", "On Hold", "Cancelled", "Pending", "Completed"]
CURRENCY_OPTIONS = ["INR", "USD", "EUR", "GBP", "AED", "Other"]


# ==============================
# Excel Utilities
# ==============================

def initialize_excel_file():
    """Create the Excel file and required sheets if they don't exist."""
    if not os.path.exists(EXCEL_FILE):
        # Create new file with all sheets and correct columns
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            for sheet_name, cfg in SHEETS_CONFIG.items():
                df = pd.DataFrame(columns=cfg["columns"])
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        # Ensure each sheet exists and has required columns
        try:
            xl = pd.ExcelFile(EXCEL_FILE, engine="openpyxl")
            existing_sheets = xl.sheet_names
        except Exception:
            # If file is corrupted or unreadable, recreate it
            with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
                for sheet_name, cfg in SHEETS_CONFIG.items():
                    df = pd.DataFrame(columns=cfg["columns"])
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            return

        # Update or add sheets as needed
        for sheet_name, cfg in SHEETS_CONFIG.items():
            required_cols = cfg["columns"]

            if sheet_name in existing_sheets:
                df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, engine="openpyxl")

                # Add any missing required columns
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = ""

                # Keep existing extra columns, but order required ones first
                extra_cols = [c for c in df.columns if c not in required_cols]
                df = df[required_cols + extra_cols]

                # Save back the updated sheet
                with pd.ExcelWriter(
                    EXCEL_FILE,
                    engine="openpyxl",
                    mode="a",
                    if_sheet_exists="replace",
                ) as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Sheet missing → create empty sheet
                df = pd.DataFrame(columns=required_cols)
                with pd.ExcelWriter(
                    EXCEL_FILE,
                    engine="openpyxl",
                    mode="a",
                ) as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)


def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Load a sheet into a DataFrame. Return empty DF with proper columns if missing."""
    initialize_excel_file()
    cfg = SHEETS_CONFIG.get(sheet_name)
    columns = cfg["columns"] if cfg else None

    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, engine="openpyxl")
    except ValueError:
        # Sheet doesn't exist; create empty
        df = pd.DataFrame(columns=columns)
    except FileNotFoundError:
        initialize_excel_file()
        df = pd.DataFrame(columns=columns)

    # Ensure at least all required columns exist
    if columns:
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        extra_cols = [c for c in df.columns if c not in columns]
        df = df[columns + extra_cols]

    return df


def save_sheet(sheet_name: str, df: pd.DataFrame):
    """Save a DataFrame back to the specific sheet in the Excel file."""
    initialize_excel_file()
    with pd.ExcelWriter(
        EXCEL_FILE,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace",
    ) as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def generate_new_id(df: pd.DataFrame) -> int:
    """Generate a new integer ID based on the current max ID in the sheet."""
    if df.empty or "id" not in df.columns:
        return 1

    try:
        numeric_ids = pd.to_numeric(df["id"], errors="coerce")
        max_id = numeric_ids.max()
        if pd.isna(max_id):
            return 1
        return int(max_id) + 1
    except Exception:
        return 1


def get_sheet_name_from_booking_type(booking_type: str) -> str:
    """Map booking type to sheet name (they are the same in this design)."""
    return booking_type


# ==============================
# Helper Functions
# ==============================

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


def render_summary_metrics(df: pd.DataFrame):
    """Show basic summary metrics for the current booking type."""
    st.subheader("Summary")

    total_bookings = len(df)
    total_amount = pd.to_numeric(df.get("total_amount", pd.Series([])), errors="coerce").sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total bookings", int(total_bookings))
    col2.metric("Total amount", f"{total_amount:,.2f}")
    # Status counts
    status_counts = df.get("status", pd.Series([])).value_counts()
    top_status = status_counts.index[0] if not status_counts.empty else "N/A"
    top_status_count = int(status_counts.iloc[0]) if not status_counts.empty else 0
    col3.metric(f"Top status", f"{top_status} ({top_status_count})")


def filtered_dataframe_ui(df: pd.DataFrame, booking_type: str) -> pd.DataFrame:
    """Show filter UI and return filtered DataFrame."""
    if df.empty:
        st.info(f"No {booking_type} bookings found.")
        return df

    with st.expander("Filters", expanded=True):
        col1, col2 = st.columns(2)

        # Filter by date range (travel_start_date)
        with col1:
            date_filter_field = st.selectbox(
                "Filter by date field",
                ["travel_start_date", "booking_date"],
                help="Choose which date field to filter on.",
            )

            date_series = pd.to_datetime(df[date_filter_field], errors="coerce")
            min_date = date_series.min().date() if not date_series.dropna().empty else dt.date.today()
            max_date = date_series.max().date() if not date_series.dropna().empty else dt.date.today()

            start_date, end_date = st.date_input(
                "Date range",
                value=(min_date, max_date),
                help="Filter records between these dates (inclusive).",
            )

        with col2:
            client_name_filter = st.text_input("Search by client name (contains)")
            status_options = ["All"] + sorted([s for s in df["status"].dropna().unique().tolist()])
            status_filter = st.selectbox("Filter by status", status_options)

            # PNR field only for types that have PNR
            pnr_filter = ""
            if booking_type in ["Flight", "Train", "Bus"]:
                pnr_filter = st.text_input("Search by PNR (exact match)")

    # Apply filters
    filtered = df.copy()

    # Date filter
    date_series = pd.to_datetime(filtered[date_filter_field], errors="coerce")
    mask = (date_series.dt.date >= start_date) & (date_series.dt.date <= end_date)
    filtered = filtered[mask]

    # Client name filter
    if client_name_filter:
        filtered = filtered[
            filtered["client_name"].astype(str).str.contains(client_name_filter, case=False, na=False)
        ]

    # Status filter
    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]

    # PNR filter
    if pnr_filter and booking_type in ["Flight", "Train", "Bus"]:
        if "pnr" in filtered.columns:
            filtered = filtered[filtered["pnr"].astype(str) == pnr_filter]

    return filtered


def download_buttons(df: pd.DataFrame, label_prefix: str = "Download"):
    """Show download buttons for Excel and CSV."""
    if df.empty:
        return

    col1, col2 = st.columns(2)

    with col1:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"{label_prefix} as CSV",
            data=csv_data,
            file_name=f"{label_prefix.replace(' ', '_').lower()}.csv",
            mime="text/csv",
        )

    with col2:
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
        towrite.seek(0)
        st.download_button(
            label=f"{label_prefix} as Excel",
            data=towrite,
            file_name=f"{label_prefix.replace(' ', '_').lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ==============================
# Forms: Create / Edit
# ==============================

def common_fields(booking_type: str, existing: Optional[pd.Series] = None) -> Dict:
    """Render common fields for all booking types and return values."""
    existing = existing or {}

    client_name = st.text_input(
        "Client name",
        value=existing.get("client_name", ""),
    )
    client_contact = st.text_input(
        "Client contact",
        value=existing.get("client_contact", ""),
        help="Phone number or email.",
    )

    # booking date
    booking_date_default = parse_date(existing.get("booking_date")) or dt.date.today()
    booking_date = st.date_input("Booking date", value=booking_date_default)

    # travel start / end dates
    travel_start_default = parse_date(existing.get("travel_start_date")) or dt.date.today()
    travel_start_date = st.date_input("Travel start date", value=travel_start_default)

    travel_end_default = parse_date(existing.get("travel_end_date")) or travel_start_default
    travel_end_date = st.date_input(
        "Travel end date",
        value=travel_end_default,
        help="Use same as start date for one-way / same-day travel.",
    )

    total_amount_default = 0.0
    try:
        total_amount_default = float(existing.get("total_amount", 0) or 0)
    except Exception:
        total_amount_default = 0.0

    total_amount = st.number_input(
        "Total amount",
        min_value=0.0,
        value=total_amount_default,
        step=100.0,
    )

    currency_default = existing.get("currency", "INR")
    if currency_default not in CURRENCY_OPTIONS:
        CURRENCY_OPTIONS.append(currency_default)

    currency = st.selectbox("Currency", CURRENCY_OPTIONS, index=CURRENCY_OPTIONS.index(currency_default))

    vendor = st.text_input(
        "Vendor (airline / hotel / operator / train provider)",
        value=existing.get("vendor", ""),
    )

    status_default = existing.get("status", STATUS_OPTIONS[0])
    if status_default not in STATUS_OPTIONS:
        STATUS_OPTIONS.append(status_default)

    status = st.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(status_default))

    remarks = st.text_area("Remarks", value=existing.get("remarks", ""))

    return {
        "booking_type": booking_type,
        "client_name": client_name,
        "client_contact": client_contact,
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
    existing = existing or {}

    pnr = st.text_input("PNR", value=existing.get("pnr", ""))
    airline = st.text_input("Airline", value=existing.get("airline", ""))
    flight_number = st.text_input("Flight number", value=existing.get("flight_number", ""))
    from_city = st.text_input("From city", value=existing.get("from_city", ""))
    to_city = st.text_input("To city", value=existing.get("to_city", ""))

    dep_dt_existing = parse_datetime(existing.get("departure_datetime"))
    dep_date_default = dep_dt_existing.date() if dep_dt_existing else dt.date.today()
    dep_time_default = dep_dt_existing.time() if dep_dt_existing else dt.time(9, 0)

    arr_dt_existing = parse_datetime(existing.get("arrival_datetime"))
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

    cabin_class = st.text_input("Cabin class", value=existing.get("cabin_class", ""))
    ticket_number = st.text_input("Ticket number", value=existing.get("ticket_number", ""))

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
    existing = existing or {}

    city = st.text_input("City", value=existing.get("city", ""))
    hotel_name = st.text_input("Hotel name", value=existing.get("hotel_name", ""))

    checkin_default = parse_date(existing.get("checkin_date")) or dt.date.today()
    checkout_default = parse_date(existing.get("checkout_date")) or (checkin_default + dt.timedelta(days=1))

    col1, col2 = st.columns(2)
    with col1:
        checkin_date = st.date_input("Check-in date", value=checkin_default)
    with col2:
        checkout_date = st.date_input("Check-out date", value=checkout_default)

    nights_default = (checkout_date - checkin_date).days
    try:
        nights_existing = int(existing.get("nights", nights_default) or nights_default)
    except Exception:
        nights_existing = nights_default

    nights = st.number_input(
        "Nights",
        min_value=0,
        value=nights_existing,
        step=1,
    )

    room_type = st.text_input("Room type", value=existing.get("room_type", ""))
    confirmation_number = st.text_input(
        "Confirmation number",
        value=existing.get("confirmation_number", ""),
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
    existing = existing or {}

    pnr = st.text_input("PNR", value=existing.get("pnr", ""))
    train_name = st.text_input("Train name", value=existing.get("train_name", ""))
    train_number = st.text_input("Train number", value=existing.get("train_number", ""))
    from_station = st.text_input("From station", value=existing.get("from_station", ""))
    to_station = st.text_input("To station", value=existing.get("to_station", ""))

    dep_dt_existing = parse_datetime(existing.get("departure_datetime"))
    dep_date_default = dep_dt_existing.date() if dep_dt_existing else dt.date.today()
    dep_time_default = dep_dt_existing.time() if dep_dt_existing else dt.time(9, 0)

    dep_date = st.date_input("Departure date", value=dep_date_default)
    dep_time = st.time_input("Departure time", value=dep_time_default)
    departure_datetime = dt.datetime.combine(dep_date, dep_time).isoformat(sep=" ")

    train_class = st.text_input("Class", value=existing.get("class", ""))
    coach = st.text_input("Coach", value=existing.get("coach", ""))
    seat_or_berth = st.text_input("Seat/Berth", value=existing.get("seat_or_berth", ""))

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
    existing = existing or {}

    pnr = st.text_input("PNR", value=existing.get("pnr", ""))
    operator_name = st.text_input("Operator name", value=existing.get("operator_name", ""))
    from_city = st.text_input("From city", value=existing.get("from_city", ""))
    to_city = st.text_input("To city", value=existing.get("to_city", ""))

    dep_dt_existing = parse_datetime(existing.get("departure_datetime"))
    dep_date_default = dep_dt_existing.date() if dep_dt_existing else dt.date.today()
    dep_time_default = dep_dt_existing.time() if dep_dt_existing else dt.time(21, 0)

    arr_dt_existing = parse_datetime(existing.get("arrival_datetime"))
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

    seat_number = st.text_input("Seat number", value=existing.get("seat_number", ""))
    bus_type = st.text_input("Bus type (AC/Non-AC, Sleeper/Seater, etc.)", value=existing.get("bus_type", ""))

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


# ==============================
# CRUD Actions
# ==============================

def create_booking(booking_type: str):
    sheet_name = get_sheet_name_from_booking_type(booking_type)
    df = load_sheet(sheet_name)

    st.subheader(f"Create new {booking_type} booking")

    with st.form(f"create_{booking_type}_form"):
        common_data = common_fields(booking_type)
        if booking_type == "Flight":
            specific_data = flight_fields()
        elif booking_type == "Hotel":
            specific_data = hotel_fields()
        elif booking_type == "Train":
            specific_data = train_fields()
        elif booking_type == "Bus":
            specific_data = bus_fields()
        else:
            specific_data = {}

        submitted = st.form_submit_button("Create booking")

        if submitted:
            errors = []
            if not common_data["client_name"]:
                errors.append("Client name is required.")
            if common_data["total_amount"] < 0:
                errors.append("Total amount cannot be negative.")

            if errors:
                st.error("\n".join(errors))
            else:
                new_id = generate_new_id(df)
                new_record = {"id": new_id}
                new_record.update(common_data)
                new_record.update(specific_data)

                df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
                save_sheet(sheet_name, df)
                st.success(f"{booking_type} booking created successfully with ID: {new_id}")


def view_bookings(booking_type: str):
    sheet_name = get_sheet_name_from_booking_type(booking_type)
    df = load_sheet(sheet_name)

    st.subheader(f"View {booking_type} bookings")

    if df.empty:
        st.info(f"No {booking_type} bookings found.")
        return

    render_summary_metrics(df)
    filtered = filtered_dataframe_ui(df, booking_type)
    st.write("### Results")
    st.dataframe(filtered, use_container_width=True)

    download_buttons(filtered, label_prefix=f"{booking_type}_bookings")


def edit_booking(booking_type: str):
    sheet_name = get_sheet_name_from_booking_type(booking_type)
    df = load_sheet(sheet_name)

    st.subheader(f"Edit {booking_type} booking")

    if df.empty:
        st.info(f"No {booking_type} bookings found to edit.")
        return

    # Optional PNR filter to narrow options
    pnr_filter = ""
    if booking_type in ["Flight", "Train", "Bus"] and "pnr" in df.columns:
        pnr_filter = st.text_input("Filter by PNR (optional)")

    df_filtered = df.copy()
    if pnr_filter and "pnr" in df.columns:
        df_filtered = df_filtered[df_filtered["pnr"].astype(str) == pnr_filter]

    if df_filtered.empty:
        st.info("No records found with the given filter.")
        return

    # Select booking by ID
    df_filtered["id_display"] = df_filtered["id"].astype(str) + " | " + df_filtered["client_name"].astype(str)
    id_options = df_filtered["id"].tolist()
    id_display_options = df_filtered["id_display"].tolist()

    selected_display = st.selectbox("Select booking to edit (ID | Client name)", id_display_options)
    selected_index = id_display_options.index(selected_display)
    selected_id = id_options[selected_index]

    record = df[df["id"] == selected_id]
    if record.empty:
        st.error("Selected booking ID not found.")
        return

    record_series = record.iloc[0]

    with st.form(f"edit_{booking_type}_form"):
        st.markdown(f"**Editing ID:** {selected_id}")
        common_data = common_fields(booking_type, existing=record_series)

        if booking_type == "Flight":
            specific_data = flight_fields(existing=record_series)
        elif booking_type == "Hotel":
            specific_data = hotel_fields(existing=record_series)
        elif booking_type == "Train":
            specific_data = train_fields(existing=record_series)
        elif booking_type == "Bus":
            specific_data = bus_fields(existing=record_series)
        else:
            specific_data = {}

        submitted = st.form_submit_button("Save changes")

        if submitted:
            errors = []
            if not common_data["client_name"]:
                errors.append("Client name is required.")
            if common_data["total_amount"] < 0:
                errors.append("Total amount cannot be negative.")

            if errors:
                st.error("\n".join(errors))
            else:
                # Update record in DataFrame
                for key, val in common_data.items():
                    df.loc[df["id"] == selected_id, key] = val
                for key, val in specific_data.items():
                    if key in df.columns:
                        df.loc[df["id"] == selected_id, key] = val

                save_sheet(sheet_name, df)
                st.success(f"{booking_type} booking with ID {selected_id} updated successfully.")


def delete_booking(booking_type: str):
    sheet_name = get_sheet_name_from_booking_type(booking_type)
    df = load_sheet(sheet_name)

    st.subheader(f"Delete {booking_type} booking")

    if df.empty:
        st.info(f"No {booking_type} bookings found to delete.")
        return

    df["id_display"] = df["id"].astype(str) + " | " + df["client_name"].astype(str)
    id_options = df["id"].tolist()
    id_display_options = df["id_display"].tolist()

    selected_display = st.selectbox("Select booking to delete (ID | Client name)", id_display_options)
    selected_index = id_display_options.index(selected_display)
    selected_id = id_options[selected_index]

    record = df[df["id"] == selected_id]
    if record.empty:
        st.error("Selected booking ID not found.")
        return

    st.write("### Booking details")
    st.dataframe(record.drop(columns=["id_display"], errors="ignore"), use_container_width=True)

    st.warning("This action cannot be undone.")

    confirm = st.checkbox("Yes, I really want to delete this booking.")
    if st.button("Delete booking", disabled=not confirm):
        if not confirm:
            st.info("Please confirm deletion by ticking the checkbox.")
            return

        df = df[df["id"] != selected_id]
        # Drop helper column if present
        if "id_display" in df.columns:
            df = df.drop(columns=["id_display"])
        save_sheet(sheet_name, df)
        st.success(f"{booking_type} booking with ID {selected_id} deleted successfully.")


# ==============================
# Main App
# ==============================

def main():
    st.set_page_config(
        page_title="Travel Booking Record Keeper",
        page_icon="✈️",
        layout="wide",
    )

    st.title("Travel Booking Record Keeper")
    st.caption("Manage Flight, Hotel, Train, and Bus bookings using Excel as the database.")

    # Sidebar navigation
    st.sidebar.header("Navigation")
    booking_type = st.sidebar.selectbox(
        "Booking Type",
        ["Flight", "Hotel", "Train", "Bus"],
    )

    action = st.sidebar.radio(
        "Action",
        ["Create", "View", "Edit", "Delete"],
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "Tip: Keep the Excel file closed while using this app to avoid file access issues."
    )

    # Initialize file/sheets (safe if called multiple times)
    initialize_excel_file()

    # Route to appropriate action
    if action == "Create":
        create_booking(booking_type)
    elif action == "View":
        view_bookings(booking_type)
    elif action == "Edit":
        edit_booking(booking_type)
    elif action == "Delete":
        delete_booking(booking_type)
    else:
        st.error("Unknown action.")


if __name__ == "__main__":
    main()
