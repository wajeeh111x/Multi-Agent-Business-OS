
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User

from app.schemas.document import DocumentResponse
from app.services.document_service import save_document

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post(
    "/upload",
    response_model=DocumentResponse
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = save_document(
        db,
        file,
        current_user.id
    )

    return document