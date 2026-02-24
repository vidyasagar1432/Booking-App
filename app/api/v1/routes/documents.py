import os
import shutil
from urllib.parse import quote
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()
UPLOADS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
    "uploads",
)
os.makedirs(UPLOADS_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


def _safe_booking_dir(booking_id: str) -> str:
    normalized = booking_id.strip()
    if not normalized or any(sep in normalized for sep in ("/", "\\", "..")):
        raise HTTPException(status_code=400, detail="Invalid booking id")
    return os.path.join(UPLOADS_DIR, normalized)


def _safe_file_path(booking_id: str, filename: str) -> str:
    safe_name = os.path.basename((filename or "").strip())
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    return os.path.join(_safe_booking_dir(booking_id), safe_name)


def _validate_extension(filename: str) -> None:
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")


@router.post("/{booking_id}")
async def upload_booking_document(booking_id: str, file: UploadFile = File(...)):
    booking_dir = _safe_booking_dir(booking_id)
    os.makedirs(booking_dir, exist_ok=True)
    safe_name = os.path.basename((file.filename or "").strip())
    _validate_extension(safe_name)
    file_path = _safe_file_path(booking_id, safe_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": safe_name, "message": "Uploaded successfully"}


@router.get("/{booking_id}")
async def list_booking_documents(booking_id: str):
    booking_dir = _safe_booking_dir(booking_id)
    if not os.path.exists(booking_dir):
        return []

    files = sorted(f for f in os.listdir(booking_dir) if os.path.isfile(os.path.join(booking_dir, f)))
    return [
        {
            "filename": f,
            "url": f"/api/v1/documents/download/{quote(booking_id, safe='')}/{quote(f, safe='')}",
        }
        for f in files
    ]


@router.get("/download/{booking_id}/{filename:path}")
async def download_booking_document(booking_id: str, filename: str):
    file_path = _safe_file_path(booking_id, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@router.delete("/{booking_id}/{filename:path}")
async def delete_booking_document(booking_id: str, filename: str):
    file_path = _safe_file_path(booking_id, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": "Deleted successfully"}
    raise HTTPException(status_code=404, detail="File not found")
