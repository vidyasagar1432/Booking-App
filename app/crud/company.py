from typing import Optional, List, Tuple
from datetime import datetime
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.domain import Company, Employee

async def get_all_companies(session: AsyncSession, 
                            search: str = "", 
                            offset: int = 0, 
                            limit: int = 100,
                            include_inactive: bool = False,
                            sort_by: str = "created_at",
                            order: str = "desc") -> Tuple[List[Company], int]:
    statement = select(Company)
    if not include_inactive:
        statement = statement.where(Company.is_active == True)
    if search:
        statement = statement.where(Company.name.ilike(f"%{search}%"))
    
    count_stmt = select(func.count()).select_from(statement.subquery())
    count_res = await session.execute(count_stmt)
    total_count = count_res.scalar_one()
    
    sort_attr = getattr(Company, sort_by, Company.created_at)
    if order == "desc":
        statement = statement.order_by(sort_attr.desc())
    else:
        statement = statement.order_by(sort_attr.asc())
        
    res = await session.execute(statement.offset(offset).limit(limit))
    results = res.scalars().all()
    
    return list(results), total_count

async def get_company_by_id(session: AsyncSession, company_id: int) -> Optional[Company]:
    res = await session.execute(select(Company).where(Company.id == company_id))
    return res.scalar_one_or_none()

async def get_company_by_name(session: AsyncSession, name: str) -> Optional[Company]:
    res = await session.execute(select(Company).where(Company.name.ilike(name)))
    return res.scalar_one_or_none()

async def create_company(session: AsyncSession, company: Company) -> Company:
    session.add(company)
    await session.flush()
    await session.refresh(company)
    return company

async def update_company(session: AsyncSession, company_id: int, data: dict) -> Optional[Company]:
    c = await get_company_by_id(session, company_id)
    if c:
        for k, v in data.items():
            if hasattr(c, k):
                setattr(c, k, v)
        c.updated_at = datetime.utcnow()
        session.add(c)
        await session.flush()
        await session.refresh(c)
    return c

async def delete_company(session: AsyncSession, company_id: int, soft_delete: bool = True) -> bool:
    c = await get_company_by_id(session, company_id)
    if not c:
        return False
    if soft_delete:
        c.is_active = False
        c.updated_at = datetime.utcnow()
        session.add(c)
    else:
        employees_res = await session.execute(select(Employee).where(Employee.company_id == company_id))
        employees = employees_res.scalars().all()
        for emp in employees:
            await session.delete(emp)
        await session.delete(c)
    
    await session.flush()
    return True
