import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException


router = APIRouter(
    prefix="/business",
    tags=["Business Intelligence"]
)


BUSINESS_UPLOAD_DIR = "uploads/business"


ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls"
}


os.makedirs(
    BUSINESS_UPLOAD_DIR,
    exist_ok=True
)


@router.post("/datasets/upload")
def upload_business_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Only CSV and Excel files are allowed."
            )
        )

    dataset_id = str(uuid.uuid4())

    safe_filename = (
        f"{dataset_id}_{file.filename}"
    )

    filepath = os.path.join(
        BUSINESS_UPLOAD_DIR,
        safe_filename
    )

    try:

        with open(filepath, "wb") as buffer:

            while True:

                chunk = file.file.read(1024 * 1024)

                if not chunk:
                    break

                buffer.write(chunk)

    except Exception as e:

        if os.path.exists(filepath):
            os.remove(filepath)

        raise HTTPException(
            status_code=500,
            detail=f"Dataset upload failed: {str(e)}"
        )

    return {
        "message": "Business dataset uploaded successfully.",
        "dataset_id": dataset_id,
        "filename": file.filename,
        "stored_filename": safe_filename,
        "filepath": filepath
    }