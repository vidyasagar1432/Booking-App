from typing import Dict, List, Tuple

DATA_FILE = "travel_bookings_v2.csv"

COMMON_FIELDS: List[Tuple[str, str]] = [
    ("Client Name", "client_name"),
    ("Client Contact", "client_contact"),
    ("Number of Passengers", "number_of_passengers"),
    ("Booking Date", "booking_date"),
    ("Travel Start Date", "travel_start_date"),
    ("Travel End Date", "travel_end_date"),
    ("Total Amount", "total_amount"),
    ("Currency", "currency"),
    ("Vendor", "vendor"),
    ("Status", "status"),
    ("Remarks", "remarks"),
]

BOOKING_FIELDS: Dict[str, List[Tuple[str, str]]] = {
    "Flight": [
        ("PNR", "pnr"),
        ("Airline", "airline"),
        ("Flight Number", "flight_number"),
        ("From City", "from_city"),
        ("To City", "to_city"),
        ("Departure Time", "departure_time"),
        ("Arrival Time", "arrival_time"),
        ("Cabin Class", "cabin_class"),
        ("Ticket Number", "ticket_number"),
    ],
    "Hotel": [
        ("City", "city"),
        ("Hotel Name", "hotel_name"),
        ("Check-in Date", "checkin_date"),
        ("Check-out Date", "checkout_date"),
        ("Room Type", "room_type"),
        ("Confirmation Number", "confirmation_number"),
    ],
    "Train": [
        ("PNR", "pnr"),
        ("Train Name", "train_name"),
        ("Train Number", "train_number"),
        ("From Station", "from_station"),
        ("To Station", "to_station"),
        ("Departure Time", "departure_time"),
        ("Class", "train_class"),
        ("Coach", "coach"),
        ("Seat/Berth", "seat_or_berth"),
    ],
    "Bus": [
        ("PNR", "pnr"),
        ("Operator", "operator_name"),
        ("From City", "from_city"),
        ("To City", "to_city"),
        ("Departure Time", "departure_time"),
        ("Arrival Time", "arrival_time"),
        ("Seat Number", "seat_number"),
        ("Bus Type", "bus_type"),
    ],
}

STATUS_OPTIONS = ["Confirmed", "On Hold", "Cancelled", "Pending", "Completed"]
CURRENCY_OPTIONS = ["INR", "USD", "EUR", "GBP", "AED", "Other"]

ALL_COLUMNS = [
    "booking_id",
    "booking_type",
    *[field_key for _, field_key in COMMON_FIELDS],
    *sorted({field_key for fields in BOOKING_FIELDS.values() for _, field_key in fields}),
]
