from typing import Optional, List, Tuple, Any
from datetime import datetime
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.domain import Employee, Company, Booking, BookingParticipant
from app.crud.company import get_company_by_name

async def get_all_employees(session: AsyncSession,
                            search: str = "",
                            company_id: Optional[int] = None,
                            offset: int = 0,
                            limit: int = 100,
                            include_inactive: bool = False,
                            include_stats: bool = False,
                            sort_by: str = "created_at",
                            order: str = "desc") -> Tuple[List[Any], int]:
    # 1. Base query for employees
    stmt = select(Employee).options(selectinload(Employee.company))
    
    # 2. Filtering
    if not include_inactive:
        stmt = stmt.where(Employee.is_active == True)
    if company_id:
        stmt = stmt.where(Employee.company_id == company_id)
    if search:
        search_filter = (Employee.name.ilike(f"%{search}%")) | (Employee.phone.ilike(f"%{search}%"))
        stmt = stmt.where(search_filter)
    
    # 3. Count
    count_stmt = select(func.count(Employee.id))
    if not include_inactive:
        count_stmt = count_stmt.where(Employee.is_active == True)
    if company_id:
        count_stmt = count_stmt.where(Employee.company_id == company_id)
    if search:
        search_filter = (Employee.name.ilike(f"%{search}%")) | (Employee.phone.ilike(f"%{search}%"))
        count_stmt = count_stmt.where(search_filter)
    
    total_count = (await session.execute(count_stmt)).scalar() or 0
    
    # 4. Sorting & Pagination
    sort_attr = getattr(Employee, sort_by, Employee.created_at)
    if order == "desc":
        stmt = stmt.order_by(sort_attr.desc(), Employee.id.desc())
    else:
        stmt = stmt.order_by(sort_attr.asc(), Employee.id.asc())
        
    res = await session.execute(stmt.offset(offset).limit(limit))
    employees = list(res.scalars().all())
    
    results = []
    # 5. Stats (Optional)
    for emp in employees:
        # Convert to dict and handle relationships
        emp_data = emp.model_dump()
        if emp.company:
            emp_data["company"] = emp.company.model_dump()
            emp_data["company_name"] = emp.company.name
        else:
            emp_data["company_name"] = None
            
        if include_stats:
            stats_stmt = select(
                func.count(BookingParticipant.booking_id),
                func.sum(Booking.cost)
            ).outerjoin(Booking, BookingParticipant.booking_id == Booking.booking_id
            ).where(BookingParticipant.employee_id == emp.id)
            stats_res = await session.execute(stats_stmt)
            row = stats_res.first()
            count, spent = row if row else (0, 0)
            emp_data["booking_count"] = int(count or 0)
            emp_data["total_spent"] = float(spent or 0)
        else:
            emp_data["booking_count"] = 0
            emp_data["total_spent"] = 0.0
            
        results.append(emp_data)
            
    return results, total_count

async def get_employee_by_id(session: AsyncSession, employee_id: int) -> Optional[Employee]:
    res = await session.execute(select(Employee).options(selectinload(Employee.company)).where(Employee.id == employee_id))
    return res.scalar_one_or_none()

async def get_employee_by_phone(session: AsyncSession, phone: str) -> Optional[Employee]:
    res = await session.execute(select(Employee).options(selectinload(Employee.company)).where(Employee.phone == phone))
    return res.scalar_one_or_none()

async def upsert_employee(session: AsyncSession, name: str, phone: str,
                          company_name: Optional[str],
                          designation: Optional[str] = None,
                          email: Optional[str] = None) -> Employee:
    emp = await get_employee_by_phone(session, phone)
    if emp:
        emp.name = name or emp.name
        if designation:
            emp.designation = designation
        if email:
            emp.email = email
        emp.is_active = True 
        emp.updated_at = datetime.utcnow()
        session.add(emp)
        await session.flush()
        await session.refresh(emp)
        return emp

    company_id = None
    if company_name and company_name.strip():
        co = await get_company_by_name(session, company_name.strip())
        if not co:
            co = Company(name=company_name.strip())
            session.add(co)
            await session.flush()
            await session.refresh(co)
        company_id = co.id

    emp = Employee(name=name, phone=phone, company_id=company_id,
                   designation=designation, email=email)
    session.add(emp)
    await session.flush()
    await session.refresh(emp)
    return emp

async def create_employee(session: AsyncSession, employee: Employee) -> Employee:
    session.add(employee)
    await session.flush()
    await session.refresh(employee)
    return employee

async def update_employee(session: AsyncSession, employee_id: int, data: dict) -> Optional[Employee]:
    emp = await get_employee_by_id(session, employee_id)
    if emp:
        for k, v in data.items():
            if hasattr(emp, k):
                setattr(emp, k, v)
        emp.updated_at = datetime.utcnow()
        session.add(emp)
        await session.flush()
        await session.refresh(emp)
    return emp

async def delete_employee(session: AsyncSession, employee_id: int, soft_delete: bool = True) -> bool:
    emp = await get_employee_by_id(session, employee_id)
    if not emp:
        return False
    if soft_delete:
        emp.is_active = False
        emp.updated_at = datetime.utcnow()
        session.add(emp)
    else:
        emp.bookings = []
        session.add(emp)
        await session.delete(emp)
    await session.flush()
    return True

async def bulk_create_employees(session: AsyncSession, employees: List[Employee]) -> List[Employee]:
    session.add_all(employees)
    await session.flush()
    for e in employees:
        await session.refresh(e)
    return employees
