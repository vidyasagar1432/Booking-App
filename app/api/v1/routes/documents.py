import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

@router.post("/{booking_id}")
async def upload_booking_document(booking_id: str, file: UploadFile = File(...)):
    booking_dir = os.path.join(UPLOADS_DIR, booking_id)
    os.makedirs(booking_dir, exist_ok=True)
    file_path = os.path.join(booking_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "message": "Uploaded successfully"}

@router.get("/{booking_id}")
async def list_booking_documents(booking_id: str):
    booking_dir = os.path.join(UPLOADS_DIR, booking_id)
    if not os.path.exists(booking_dir):
        return []
    files = os.listdir(booking_dir)
    return [{"filename": f, "url": f"/api/v1/documents/download/{booking_id}/{f}"} for f in files]

@router.get("/download/{booking_id}/{filename}")
async def download_booking_document(booking_id: str, filename: str):
    file_path = os.path.join(UPLOADS_DIR, booking_id, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.delete("/{booking_id}/{filename}")
async def delete_booking_document(booking_id: str, filename: str):
    file_path = os.path.join(UPLOADS_DIR, booking_id, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": "Deleted successfully"}
    raise HTTPException(status_code=404, detail="File not found")
