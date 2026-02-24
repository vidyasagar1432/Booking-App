from app.models.domain import Booking

def booking_to_dict(b: Booking) -> dict:
    base_dict = {
        "booking_id": b.booking_id,
        "booking_type": b.booking_type,
        "booking_date": b.booking_date.isoformat() if b.booking_date else None,
        "start_datetime": b.start_datetime.isoformat() if getattr(b, "start_datetime", None) else None,
        "end_datetime": b.end_datetime.isoformat() if getattr(b, "end_datetime", None) else None,
        "cost": getattr(b, "cost", 0.0),
        "status": getattr(b, "status", "Confirmed"),
        "notes": getattr(b, "notes", None),
        "total_employees": len(b.participants) if getattr(b, "participants", None) else 0,
        "employees": [
            {
                "id": e.id, "name": e.name, "phone": e.phone, "email": e.email,
                "designation": e.designation, "company_id": e.company_id,
                "company_name": e.company.name if getattr(e, "company", None) else None,
                "id_type": e.id_type, "id_number": e.id_number
            }
            for e in getattr(b, "participants", [])
        ],
    }

    # Flatten specific subclass types dynamically to match the expected format
    if b.booking_type == "Flight" and b.flight_details:
        f = b.flight_details
        base_dict.update({
            "flight_number": f.flight_number, "airline": f.airline,
            "pnr_status": f.pnr_status, "seat_class": f.seat_class,
            "from_city": f.from_city, "to_city": f.to_city
        })
    elif b.booking_type == "Train" and b.train_details:
        t = b.train_details
        base_dict.update({
            "train_number": t.train_number, "coach_number": t.coach_number, 
            "platform": getattr(t, "platform", None), 
            "from_city": t.from_city, "to_city": t.to_city,
            "pnr_status": getattr(t, "pnr_status", None), 
            "seat_class": getattr(t, "seat_class", None)
        })
    elif b.booking_type == "Bus" and b.bus_details:
        bus = b.bus_details
        base_dict.update({
            "bus_operator": bus.bus_operator, "bus_pnr": bus.bus_pnr,
            "pickup_point": bus.pickup_point, "drop_point": bus.drop_point,
            "from_city": bus.from_city, "to_city": bus.to_city,
            "pnr_status": getattr(bus, "pnr_status", None), 
            "seat_class": getattr(bus, "seat_class", None)
        })
    elif b.booking_type == "Hotel" and b.hotel_details:
        h = b.hotel_details
        base_dict.update({
            "hotel_name": h.hotel_name, "room_type": h.room_type, 
            "hotel_address": h.hotel_address, "check_in_time": h.check_in_time, 
            "check_out_time": h.check_out_time, "from_city": h.city, "to_city": None
        })

    return base_dict
