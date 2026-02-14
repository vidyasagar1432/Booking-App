from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import model_validator
from sqlalchemy import func, or_
from sqlmodel import Field, Session, SQLModel, create_engine, select

class BookingMode(str, Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    TRAIN = "train"
    BUS = "bus"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class BookingBase(SQLModel):
    booking_mode: BookingMode
    booking_id: Optional[str] = Field(default=None, max_length=32, index=True)

    company_name: Optional[str] = Field(default=None, max_length=120)
    email: Optional[str] = Field(default=None, max_length=120)
    phone: Optional[str] = Field(default=None, max_length=30)
    vendor: Optional[str] = Field(default=None, max_length=120)
    booking_date: Optional[date] = None
    status: BookingStatus = BookingStatus.PENDING
    notes: Optional[str] = Field(default=None, max_length=500)
    total_cost: Optional[float] = Field(default=None, ge=0)

    passengers: Optional[str] = Field(default=None, max_length=500)
    passenger_count: Optional[int] = Field(default=None, ge=0)
    passenger_name: Optional[str] = Field(default=None, max_length=120)

    guests: Optional[str] = Field(default=None, max_length=500)
    guests_count: Optional[int] = Field(default=None, ge=0)
    guest_name: Optional[str] = Field(default=None, max_length=120)

    airline: Optional[str] = Field(default=None, max_length=120)
    pnr_eticket_no: Optional[str] = Field(default=None, max_length=120)
    trip_type: Optional[str] = Field(default=None, max_length=40)
    from_airport: Optional[str] = Field(default=None, max_length=120)
    to_airport: Optional[str] = Field(default=None, max_length=120)

    hotel_name: Optional[str] = Field(default=None, max_length=120)
    city: Optional[str] = Field(default=None, max_length=120)
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    number_of_nights: Optional[int] = Field(default=None, ge=0)
    room_type: Optional[str] = Field(default=None, max_length=120)
    number_of_rooms: Optional[int] = Field(default=None, ge=0)

    train_name: Optional[str] = Field(default=None, max_length=120)
    train_number: Optional[str] = Field(default=None, max_length=60)
    from_station: Optional[str] = Field(default=None, max_length=120)
    to_station: Optional[str] = Field(default=None, max_length=120)
    coach: Optional[str] = Field(default=None, max_length=60)

    bus_company: Optional[str] = Field(default=None, max_length=120)
    bus_pnr: Optional[str] = Field(default=None, max_length=120)
    from_city: Optional[str] = Field(default=None, max_length=120)
    to_city: Optional[str] = Field(default=None, max_length=120)

    departure_date: Optional[date] = None
    departure_time: Optional[str] = Field(default=None, max_length=20)
    arrival_date: Optional[date] = None
    arrival_time: Optional[str] = Field(default=None, max_length=20)
    seat_number: Optional[str] = Field(default=None, max_length=60)
    travel_class: Optional[str] = Field(default=None, max_length=60)

    @model_validator(mode="after")
    def validate_dates_and_mode(self):
        if self.check_in_date and self.check_out_date and self.check_in_date > self.check_out_date:
            raise ValueError("check_in_date must be before or equal to check_out_date")
        if self.departure_date and self.arrival_date and self.departure_date > self.arrival_date:
            raise ValueError("departure_date must be before or equal to arrival_date")
        if self.booking_mode == BookingMode.HOTEL and not (self.guest_name or self.company_name):
            raise ValueError("Hotel booking requires guest_name or company_name")
        if self.booking_mode in {BookingMode.FLIGHT, BookingMode.TRAIN, BookingMode.BUS} and not (
            self.passenger_name or self.company_name
        ):
            raise ValueError("Travel booking requires passenger_name or company_name")
        return self


class Booking(BookingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class BookingCreate(BookingBase):
    pass


class BookingUpdate(SQLModel):
    booking_mode: Optional[BookingMode] = None
    booking_id: Optional[str] = Field(default=None, max_length=32)
    company_name: Optional[str] = Field(default=None, max_length=120)
    email: Optional[str] = Field(default=None, max_length=120)
    phone: Optional[str] = Field(default=None, max_length=30)
    vendor: Optional[str] = Field(default=None, max_length=120)
    booking_date: Optional[date] = None
    status: Optional[BookingStatus] = None
    notes: Optional[str] = Field(default=None, max_length=500)
    total_cost: Optional[float] = Field(default=None, ge=0)

    passengers: Optional[str] = Field(default=None, max_length=500)
    passenger_count: Optional[int] = Field(default=None, ge=0)
    passenger_name: Optional[str] = Field(default=None, max_length=120)

    guests: Optional[str] = Field(default=None, max_length=500)
    guests_count: Optional[int] = Field(default=None, ge=0)
    guest_name: Optional[str] = Field(default=None, max_length=120)

    airline: Optional[str] = Field(default=None, max_length=120)
    pnr_eticket_no: Optional[str] = Field(default=None, max_length=120)
    trip_type: Optional[str] = Field(default=None, max_length=40)
    from_airport: Optional[str] = Field(default=None, max_length=120)
    to_airport: Optional[str] = Field(default=None, max_length=120)

    hotel_name: Optional[str] = Field(default=None, max_length=120)
    city: Optional[str] = Field(default=None, max_length=120)
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    number_of_nights: Optional[int] = Field(default=None, ge=0)
    room_type: Optional[str] = Field(default=None, max_length=120)
    number_of_rooms: Optional[int] = Field(default=None, ge=0)

    train_name: Optional[str] = Field(default=None, max_length=120)
    train_number: Optional[str] = Field(default=None, max_length=60)
    from_station: Optional[str] = Field(default=None, max_length=120)
    to_station: Optional[str] = Field(default=None, max_length=120)
    coach: Optional[str] = Field(default=None, max_length=60)

    bus_company: Optional[str] = Field(default=None, max_length=120)
    bus_pnr: Optional[str] = Field(default=None, max_length=120)
    from_city: Optional[str] = Field(default=None, max_length=120)
    to_city: Optional[str] = Field(default=None, max_length=120)

    departure_date: Optional[date] = None
    departure_time: Optional[str] = Field(default=None, max_length=20)
    arrival_date: Optional[date] = None
    arrival_time: Optional[str] = Field(default=None, max_length=20)
    seat_number: Optional[str] = Field(default=None, max_length=60)
    travel_class: Optional[str] = Field(default=None, max_length=60)

    @model_validator(mode="after")
    def validate_date_order(self):
        if self.check_in_date and self.check_out_date and self.check_in_date > self.check_out_date:
            raise ValueError("check_in_date must be before or equal to check_out_date")
        if self.departure_date and self.arrival_date and self.departure_date > self.arrival_date:
            raise ValueError("departure_date must be before or equal to arrival_date")
        return self


class BookingRead(BookingBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ConnectionManager:
    def __init__(self) -> None:
        self.active: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active.discard(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        stale_connections: list[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_json(payload)
            except Exception:
                stale_connections.append(ws)
        for ws in stale_connections:
            self.disconnect(ws)


def response_ok(data: Any, message: str = "OK", meta: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return {"success": True, "message": message, "data": data, "meta": meta or {}}


def response_error(message: str, code: str = "ERROR", details: Any = None) -> dict[str, Any]:
    return {"success": False, "error": {"code": code, "message": message, "details": details}}


def build_booking_code(mode: BookingMode) -> str:
    prefix = {
        BookingMode.FLIGHT: "FL",
        BookingMode.HOTEL: "HT",
        BookingMode.TRAIN: "TR",
        BookingMode.BUS: "BS",
    }[mode]
    return f"{prefix}{datetime.utcnow().strftime('%y%m%d%H%M%S')}{uuid4().hex[:4].upper()}"


def apply_booking_filters(statement, booking_mode: Optional[BookingMode], status: Optional[BookingStatus], search: Optional[str]):
    if booking_mode:
        statement = statement.where(Booking.booking_mode == booking_mode)
    if status:
        statement = statement.where(Booking.status == status)
    if search:
        pattern = f"%{search.strip().lower()}%"
        statement = statement.where(
            or_(
                func.lower(func.coalesce(Booking.booking_id, "")).like(pattern),
                func.lower(func.coalesce(Booking.passenger_name, "")).like(pattern),
                func.lower(func.coalesce(Booking.guest_name, "")).like(pattern),
                func.lower(func.coalesce(Booking.company_name, "")).like(pattern),
                func.lower(func.coalesce(Booking.from_airport, "")).like(pattern),
                func.lower(func.coalesce(Booking.to_airport, "")).like(pattern),
                func.lower(func.coalesce(Booking.city, "")).like(pattern),
            )
        )
    return statement


sqlite_file_name = "bookings.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}", connect_args={"check_same_thread": False})
manager = ConnectionManager()

app = FastAPI(title="Booking App API")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=response_error(str(exc.detail), "HTTP_ERROR"))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=response_error("Validation failed", "VALIDATION_ERROR", exc.errors()))


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception):
    return JSONResponse(status_code=500, content=response_error("Internal server error", "SERVER_ERROR", str(exc)))


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def live_updates(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/bookings")
def list_bookings(
    booking_mode: Optional[BookingMode] = None,
    status: Optional[BookingStatus] = None,
    search: Optional[str] = Query(default=None, min_length=1, max_length=120),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    base_statement = apply_booking_filters(select(Booking), booking_mode, status, search)
    count_statement = apply_booking_filters(select(func.count(Booking.id)), booking_mode, status, search)

    total = session.exec(count_statement).one()
    offset = (page - 1) * page_size

    bookings = session.exec(
        base_statement.order_by(Booking.created_at.desc()).offset(offset).limit(page_size)
    ).all()

    meta = {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size if total else 0,
    }
    return response_ok(bookings, "Bookings fetched", meta)


@app.post("/api/bookings", status_code=201)
async def create_booking(booking: BookingCreate, session: Session = Depends(get_session)):
    data = booking.model_dump()
    if not data.get("booking_id"):
        data["booking_id"] = build_booking_code(booking.booking_mode)

    db_booking = Booking(**data)
    session.add(db_booking)
    session.commit()
    session.refresh(db_booking)

    await manager.broadcast({"event": "booking_changed", "id": db_booking.id})
    return response_ok(db_booking, "Booking created")


@app.patch("/api/bookings/{booking_id}")
async def update_booking(booking_id: int, booking_update: BookingUpdate, session: Session = Depends(get_session)):
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    update_data = booking_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for key, value in update_data.items():
        setattr(booking, key, value)
    booking.updated_at = datetime.utcnow()

    session.add(booking)
    session.commit()
    session.refresh(booking)

    await manager.broadcast({"event": "booking_changed", "id": booking.id})
    return response_ok(booking, "Booking updated")


@app.delete("/api/bookings/{booking_id}")
async def delete_booking(booking_id: int, session: Session = Depends(get_session)):
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    session.delete(booking)
    session.commit()

    await manager.broadcast({"event": "booking_changed", "id": booking_id})
    return response_ok({"id": booking_id}, "Booking deleted")


@app.get("/api/admin/summary")
def admin_summary(session: Session = Depends(get_session)):
    total_bookings = session.exec(select(func.count(Booking.id))).one()
    total_revenue = session.exec(select(func.coalesce(func.sum(Booking.total_cost), 0.0))).one()

    mode_rows = session.exec(select(Booking.booking_mode, func.count(Booking.id)).group_by(Booking.booking_mode)).all()
    status_rows = session.exec(select(Booking.status, func.count(Booking.id)).group_by(Booking.status)).all()

    summary = {
        "total_bookings": total_bookings,
        "total_revenue": float(total_revenue or 0),
        "by_mode": {mode: count for mode, count in mode_rows},
        "by_status": {status: count for status, count in status_rows},
    }
    return response_ok(summary, "Summary fetched")
