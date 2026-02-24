import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

from app.core.config import settings
from app.api.v1.api import api_router
from app.api.websockets import manager
from app.db.session import init_db
import time
from fastapi import Request

# Configure centralized logging
logger = logging.getLogger("app.main")
logger.setLevel(logging.INFO)
if not logger.handlers:
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))
    logger.addHandler(sh)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI application...")
    await init_db()
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"REQ: {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"Welcome to {settings.PROJECT_NAME}", "docs": "/docs", "info": "Frontend index.html not found in app/static"}

async def global_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
    # This captures all routes not matched by API or /static/
    # If the user reloads a frontend route like /bookings or /employees,
    # we serve the index.html so Vue Router can handle it.
    
    # We strip any leading/trailing slashes for comparison
    clean_path = full_path.strip("/")
    
    # Don't serve index.html for missing API or static assets
    if clean_path.startswith("api") or clean_path.startswith("static"):
        raise HTTPException(status_code=404)
        
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"message": "Frontend index.html not found"}

