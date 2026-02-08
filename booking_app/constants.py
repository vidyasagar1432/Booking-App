from typing import Dict

EXCEL_FILE = "travel_bookings.xlsx"

COMMON_COLUMNS = [
    "id",
    "booking_type",
    "client_name",
    "client_contact",
    "number_of_passengers",
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

__all__ = [
    "EXCEL_FILE",
    "COMMON_COLUMNS",
    "SHEETS_CONFIG",
    "STATUS_OPTIONS",
    "CURRENCY_OPTIONS",
]
