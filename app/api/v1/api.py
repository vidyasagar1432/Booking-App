from fastapi import APIRouter
from app.api.v1.routes import companies, employees, bookings, analytics, documents, search, admin

api_router = APIRouter()
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(search.router, prefix="/search", tags=["search"])  # suggestions, search, notifications
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
