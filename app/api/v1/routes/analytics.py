import os
import io
import csv
from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from app.db.session import get_session
from app.models.domain import Booking, Company, Employee, BookingParticipant

router = APIRouter()

@router.get("")
async def analytics(type: Optional[str] = None, status: Optional[str] = None, 
                    date_from: Optional[str] = None, date_to: Optional[str] = None, 
                    detailed: bool = False,
                    session: AsyncSession = Depends(get_session)):
    
    # Safely parse dates
    dt_from = None
    if date_from and date_from.strip() and date_from != 'null':
        try:
            dt_from = date.fromisoformat(date_from)
        except ValueError:
            pass

    dt_to = None
    if date_to and date_to.strip() and date_to != 'null':
        try:
            dt_to = date.fromisoformat(date_to)
        except ValueError:
            pass

    # Base filters
    filters = []
    if type: filters.append(Booking.booking_type == type)
    if status: filters.append(Booking.status == status)
    if dt_from: filters.append(Booking.booking_date >= datetime.combine(dt_from, datetime.min.time()))
    if dt_to: filters.append(Booking.booking_date <= datetime.combine(dt_to, datetime.max.time()))

    # 1. KPIs
    async def get_kpi(stmt):
        res = await session.execute(stmt)
        return res.scalar() or 0

    total_bookings = await get_kpi(select(func.count(Booking.booking_id)).where(*filters))
    total_revenue = await get_kpi(select(func.sum(Booking.cost)).where(*filters))
    total_pax = await get_kpi(
        select(func.count(BookingParticipant.employee_id))
        .join(Booking).where(*filters)
    )
    total_employees = await get_kpi(select(func.count(Employee.id)).where(Employee.is_active == True))
    total_companies = await get_kpi(select(func.count(Company.id)).where(Company.is_active == True))
    confirmed = await get_kpi(select(func.count(Booking.booking_id)).where(Booking.status == "Confirmed", *filters))

    # 2. Charts - Monthly Revenue
    monthly_stmt = (
        select(func.strftime("%Y-%m", Booking.booking_date).label("month"), func.sum(Booking.cost))
        .where(*filters)
        .group_by("month")
        .order_by("month")
    )
    monthly_res = await session.execute(monthly_stmt)
    monthly_data = monthly_res.all()

    # 3. Charts - Booking Types
    type_stmt = (
        select(Booking.booking_type, func.count(Booking.booking_id))
        .where(*filters)
        .group_by(Booking.booking_type)
    )
    type_res = await session.execute(type_stmt)
    type_data = type_res.all()

    # 4. Charts - Statuses
    status_stmt = (
        select(Booking.status, func.count(Booking.booking_id))
        .where(*filters)
        .group_by(Booking.status)
    )
    status_res = await session.execute(status_stmt)
    status_data = status_res.all()

    # 5. Charts - Top Companies
    top_co_stmt = (
        select(Company.name, func.sum(Booking.cost))
        .join(Employee, Employee.company_id == Company.id)
        .join(BookingParticipant, BookingParticipant.employee_id == Employee.id)
        .join(Booking, Booking.booking_id == BookingParticipant.booking_id)
        .where(*filters)
        .group_by(Company.name)
        .order_by(func.sum(Booking.cost).desc())
        .limit(10 if detailed else 5)
    )
    top_co_res = await session.execute(top_co_stmt)
    top_co_data = top_co_res.all()

    # Detailed analytics
    extra_charts = {}
    if detailed:
        # Top Employees
        top_emp_stmt = (
            select(Employee.name, func.sum(Booking.cost))
            .join(BookingParticipant, BookingParticipant.employee_id == Employee.id)
            .join(Booking, Booking.booking_id == BookingParticipant.booking_id)
            .where(*filters)
            .group_by(Employee.name)
            .order_by(func.sum(Booking.cost).desc())
            .limit(10)
        )
        top_emp_res = await session.execute(top_emp_stmt)
        top_emp_data = top_emp_res.all()
        extra_charts["top_employees"] = {
            "labels": [e[0] for e in top_emp_data],
            "values": [round(float(e[1] or 0), 2) for e in top_emp_data]
        }

        # Type-specific breakdowns
        if type == "Flight" or not type:
            from app.models.domain import BookingFlight
            airline_stmt = (
                select(BookingFlight.airline, func.count(BookingFlight.booking_id))
                .join(Booking, Booking.booking_id == BookingFlight.booking_id)
                .where(*filters)
                .group_by(BookingFlight.airline)
            )
            air_res = await session.execute(airline_stmt)
            air_data = air_res.all()
            extra_charts["airlines"] = {
                "labels": [a[0] or "Unknown" for a in air_data],
                "values": [a[1] for a in air_data]
            }

        if type == "Hotel" or not type:
            from app.models.domain import BookingHotel
            hotel_stmt = (
                select(BookingHotel.hotel_name, func.count(BookingHotel.booking_id))
                .join(Booking, Booking.booking_id == BookingHotel.booking_id)
                .where(*filters)
                .group_by(BookingHotel.hotel_name)
                .limit(10)
            )
            h_res = await session.execute(hotel_stmt)
            h_data = h_res.all()
            extra_charts["hotels"] = {
                "labels": [h[0] or "Unknown" for h in h_data],
                "values": [h[1] for h in h_data]
            }

        if type == "Train" or not type:
            from app.models.domain import BookingTrain
            train_stmt = (
                select(func.concat(BookingTrain.from_city, " - ", BookingTrain.to_city), func.count(BookingTrain.booking_id))
                .join(Booking, Booking.booking_id == BookingTrain.booking_id)
                .where(*filters)
                .group_by(BookingTrain.from_city, BookingTrain.to_city)
                .limit(10)
            )
            tr_res = await session.execute(train_stmt)
            tr_data = tr_res.all()
            extra_charts["trains"] = {
                "labels": [t[0] or "Unknown" for t in tr_data],
                "values": [t[1] for t in tr_data]
            }

        if type == "Bus" or not type:
            from app.models.domain import BookingBus
            bus_stmt = (
                select(BookingBus.bus_operator, func.count(BookingBus.booking_id))
                .join(Booking, Booking.booking_id == BookingBus.booking_id)
                .where(*filters)
                .group_by(BookingBus.bus_operator)
            )
            b_res = await session.execute(bus_stmt)
            b_data = b_res.all()
            extra_charts["buses"] = {
                "labels": [b[0] or "Unknown" for b in b_data],
                "values": [b[1] for b in b_data]
            }

    db_size = 0.0
    if os.path.exists("booking.db"):
        db_size = os.path.getsize("booking.db") / 1024.0

    # 6. Charts - Daily Passengers (Last 14 days)
    today = date.today()
    start_date = today - timedelta(days=14)
    pax_stmt = (
        select(func.date(Booking.booking_date).label("date"), func.count(BookingParticipant.employee_id))
        .join(BookingParticipant, BookingParticipant.booking_id == Booking.booking_id)
        .where(Booking.booking_date >= datetime.combine(start_date, datetime.min.time()), *filters)
        .group_by("date")
        .order_by("date")
    )
    pax_res = await session.execute(pax_stmt)
    pax_data = pax_res.all()

    avg_cost = total_revenue / total_bookings if total_bookings > 0 else 0
    
    response = {
        "kpis": {
            "total_bookings": total_bookings,
            "total_revenue": round(float(total_revenue or 0), 2),
            "avg_cost": round(float(avg_cost), 2),
            "total_passengers": total_pax,
            "total_employees": total_employees,
            "total_companies": total_companies,
            "confirmed_bookings": confirmed,
            "db_size": round(db_size, 2)
        },
        "charts": {
            "monthly_revenue": {
                "labels": [m[0] for m in monthly_data],
                "values": [round(float(m[1] or 0), 2) for m in monthly_data]
            },
            "booking_types": {
                "labels": [t[0] for t in type_data],
                "values": [t[1] for t in type_data]
            },
            "statuses": {
                "labels": [s[0] for s in status_data],
                "values": [s[1] for s in status_data]
            },
            "top_companies": {
                "labels": [c[0] for c in top_co_data],
                "values": [round(float(c[1] or 0), 2) for c in top_co_data]
            },
            "daily_passengers": {
                "labels": [str(p[0]) for p in pax_data],
                "values": [p[1] for p in pax_data]
            }
        },
    }
    if extra_charts:
        response["charts"].update(extra_charts)
    return response

@router.get("/export")
async def export_analytics_summary(type: Optional[str] = None, status: Optional[str] = None, 
                                   date_from: Optional[date] = None, date_to: Optional[date] = None, 
                                   session: AsyncSession = Depends(get_session)):
    # Pass arguments explicitly to avoid misalignment
    data = await analytics(
        type=type, 
        status=status, 
        date_from=str(date_from) if date_from else None, 
        date_to=str(date_to) if date_to else None, 
        detailed=False, 
        session=session
    )
    kpis = data["kpis"]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total Bookings", kpis["total_bookings"]])
    writer.writerow(["Total Revenue", kpis["total_revenue"]])
    writer.writerow(["Total Passengers", kpis["total_passengers"]])
    writer.writerow(["Total Employees", kpis["total_employees"]])
    writer.writerow(["Total Companies", kpis["total_companies"]])
    writer.writerow(["Confirmed Bookings", kpis["confirmed_bookings"]])
    writer.writerow(["DB Size (KB)", kpis["db_size"]])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": f"attachment; filename=analytics_summary_{datetime.now().strftime('%Y%m%d')}.csv"}
    )
