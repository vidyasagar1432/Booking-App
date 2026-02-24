from typing import Optional, List, Tuple
from datetime import datetime
from sqlmodel import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.domain import (
    Booking, Company, Employee, BookingFlight, BookingTrain, BookingBus, BookingHotel
)

async def get_all_bookings(session: AsyncSession,
                           search: str = "",
                           statuses: Optional[List[str]] = None,
                           types: Optional[List[str]] = None,
                           date_from: Optional[datetime] = None,
                           date_to: Optional[datetime] = None,
                           min_cost: Optional[float] = None,
                           max_cost: Optional[float] = None,
                           sort_by: str = "booking_date",
                           order: str = "desc",
                           offset: int = 0,
                           limit: int = 100) -> Tuple[List[Booking], int]:
    
    statement = select(Booking).options(
        selectinload(Booking.participants).selectinload(Employee.company),
        selectinload(Booking.flight_details),
        selectinload(Booking.train_details),
        selectinload(Booking.bus_details),
        selectinload(Booking.hotel_details),
    )
    
    if types:
        statement = statement.where(Booking.booking_type.in_(types))
    if statuses:
        statement = statement.where(Booking.status.in_(statuses))
    if min_cost is not None:
        statement = statement.where(Booking.cost >= min_cost)
    if max_cost is not None:
        statement = statement.where(Booking.cost <= max_cost)
    if date_from:
        statement = statement.where(Booking.booking_date >= date_from)
    if date_to:
        statement = statement.where(Booking.booking_date <= date_to)
    
    if search:
        search_filter = (
            (Booking.booking_id.ilike(f"%{search}%")) |
            (Booking.notes.ilike(f"%{search}%")) |
            (Booking.participants.any(Employee.name.ilike(f"%{search}%"))) |
            (Booking.participants.any(Employee.company.has(Company.name.ilike(f"%{search}%"))))
        )
        statement = statement.where(search_filter)
        
    count_stmt = select(func.count()).select_from(statement.subquery())
    count_res = await session.execute(count_stmt)
    total_count = count_res.scalar_one()
    
    sort_attr = getattr(Booking, sort_by, Booking.booking_date)
    if order == "desc":
        statement = statement.order_by(sort_attr.desc(), Booking.booking_date.desc())
    else:
        statement = statement.order_by(sort_attr.asc(), Booking.booking_date.asc())

    res = await session.execute(statement.offset(offset).limit(limit))
    return list(res.scalars().all()), total_count


async def get_booking_by_id(session: AsyncSession, booking_id: str) -> Optional[Booking]:
    stmt = select(Booking).options(
        selectinload(Booking.participants).selectinload(Employee.company),
        selectinload(Booking.flight_details),
        selectinload(Booking.train_details),
        selectinload(Booking.bus_details),
        selectinload(Booking.hotel_details),
    ).where(Booking.booking_id == booking_id)
    res = await session.execute(stmt)
    return res.scalar_one_or_none()

async def create_booking(session: AsyncSession, booking: Booking) -> Booking:
    session.add(booking)
    await session.flush()
    await session.refresh(booking)
    return await get_booking_by_id(session, booking.booking_id)

async def update_booking(session: AsyncSession, booking_id: str, data: dict) -> Optional[Booking]:
    b = await get_booking_by_id(session, booking_id)
    if b:
        for k, v in data.items():
            if hasattr(b, k):
                setattr(b, k, v)
        session.add(b)
        await session.flush()
        await session.refresh(b)
        return await get_booking_by_id(session, booking_id)
    return None

async def delete_booking(session: AsyncSession, booking_id: str) -> bool:
    b = await get_booking_by_id(session, booking_id)
    if not b:
        return False
        
    b.participants = []
    session.add(b)
    
    if b.flight_details: await session.delete(b.flight_details)
    if b.train_details: await session.delete(b.train_details)
    if b.bus_details: await session.delete(b.bus_details)
    if b.hotel_details: await session.delete(b.hotel_details)
    
    await session.delete(b)
    await session.flush()
    return True

async def get_bookings_for_employee(session: AsyncSession, employee_id: int) -> List[Booking]:
    stmt = select(Booking).options(
        selectinload(Booking.participants).selectinload(Employee.company),
        selectinload(Booking.flight_details),
        selectinload(Booking.train_details),
        selectinload(Booking.bus_details),
        selectinload(Booking.hotel_details),
    ).where(Booking.participants.any(Employee.id == employee_id))
    res = await session.execute(stmt)
    return list(res.scalars().all())

async def get_suggestions(session: AsyncSession, field: str, q: str) -> List[str]:
    # Determine which table the field belongs to
    model = None
    attr_name = field

    if field in ["airline", "from_city", "to_city"]:
        model = BookingFlight
    elif field in ["train_number"]:
        model = BookingTrain
    elif field in ["bus_operator"]:
        model = BookingBus
    elif field in ["hotel_name", "city"]:
        model = BookingHotel
    elif field == "employee_name":
        model = Employee
        attr_name = "name"
    elif field == "employee_phone":
        model = Employee
        attr_name = "phone"
    
    if not model:
        # Fallback for cities if not flight-specific
        if field in ["from_city", "to_city"]:
            model = BookingFlight
        else:
            return []

    attr = getattr(model, attr_name, None)
    if not attr: return []

    stmt = select(attr).distinct().where(attr.ilike(f"%{q}%")).limit(10)
    res = await session.execute(stmt)
    return list(res.scalars().all())
