import uuid
from typing import Optional, List
from datetime import datetime, date
from sqlmodel import Field, SQLModel, Relationship

def generate_booking_id() -> str:
    uid = uuid.uuid4().hex[:8].upper()
    year = date.today().year
    return f"BK-{year}-{uid}"

# ----------------- Companies -----------------

class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    industry: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    employees: List["Employee"] = Relationship(back_populates="company")

# ----------------- Employees (Participants) -----------------

class BookingParticipant(SQLModel, table=True):
    booking_id: str = Field(foreign_key="booking.booking_id", primary_key=True)
    employee_id: int = Field(foreign_key="employee.id", primary_key=True)

class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: Optional[int] = Field(default=None, foreign_key="company.id", index=True)
    name: str = Field(index=True)
    designation: Optional[str] = None
    phone: str = Field(index=True)
    email: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    company: Optional[Company] = Relationship(back_populates="employees")
    bookings: List["Booking"] = Relationship(back_populates="participants", link_model=BookingParticipant)

    @property
    def company_name(self) -> Optional[str]:
        return self.company.name if self.company else None

# ----------------- Normalized Bookings -----------------

class Booking(SQLModel, table=True):
    booking_id: str = Field(
        default_factory=generate_booking_id,
        primary_key=True,
        index=True,
        unique=True,
    )
    booking_type: str  # Flight, Train, Bus, Hotel
    booking_date: datetime = Field(default_factory=datetime.utcnow)
    start_datetime: datetime
    end_datetime: datetime
    cost: float = Field(default=0.0)
    status: str = Field(default="Confirmed")  # Pending, Confirmed, Cancelled, Completed
    notes: Optional[str] = None

    # Polymorphic 1-to-1 relationships
    flight_details: Optional["BookingFlight"] = Relationship(back_populates="booking")
    train_details: Optional["BookingTrain"] = Relationship(back_populates="booking")
    bus_details: Optional["BookingBus"] = Relationship(back_populates="booking")
    hotel_details: Optional["BookingHotel"] = Relationship(back_populates="booking")

    participants: List[Employee] = Relationship(back_populates="bookings", link_model=BookingParticipant)

class BookingFlight(SQLModel, table=True):
    booking_id: str = Field(foreign_key="booking.booking_id", primary_key=True)
    flight_number: Optional[str] = None
    airline: Optional[str] = None
    pnr_status: Optional[str] = None
    seat_class: Optional[str] = None
    from_city: Optional[str] = None
    to_city: Optional[str] = None

    booking: Booking = Relationship(back_populates="flight_details")

class BookingTrain(SQLModel, table=True):
    booking_id: str = Field(foreign_key="booking.booking_id", primary_key=True)
    train_number: Optional[str] = None
    coach_number: Optional[str] = None
    platform: Optional[str] = None
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    pnr_status: Optional[str] = None
    seat_class: Optional[str] = None

    booking: Booking = Relationship(back_populates="train_details")

class BookingBus(SQLModel, table=True):
    booking_id: str = Field(foreign_key="booking.booking_id", primary_key=True)
    bus_operator: Optional[str] = None
    bus_pnr: Optional[str] = None
    pickup_point: Optional[str] = None
    drop_point: Optional[str] = None
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    pnr_status: Optional[str] = None
    seat_class: Optional[str] = None

    booking: Booking = Relationship(back_populates="bus_details")

class BookingHotel(SQLModel, table=True):
    booking_id: str = Field(foreign_key="booking.booking_id", primary_key=True)
    hotel_name: Optional[str] = None
    room_type: Optional[str] = None
    hotel_address: Optional[str] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    city: Optional[str] = None  # Replaces to/from city for consistency in hotel

    booking: Booking = Relationship(back_populates="hotel_details")
