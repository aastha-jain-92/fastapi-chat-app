from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.s3_service import S3Service
from app.utils.helpers import generate_file_name

router = APIRouter()

ALLOWED_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
]

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type"
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large"
        )

    file_name = f"uploads/{generate_file_name(file.filename)}"

    file.file.seek(0)

    file_url = S3Service.upload_file(
        file.file,
        file_name,
        file.content_type
    )

    return {
        "success": True,
        "url": file_url
    }