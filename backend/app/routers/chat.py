from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User

from app.schemas.chat import ChatRequest, ChatResponse

from app.services.chat_service import (
    save_message,
    get_chat_history
)

from app.agents.agent import run_agent

router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"]
)


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Save user's message
    save_message(
        db=db,
        user_id=current_user.id,
        role="user",
        message=request.message
    )

    # Load previous conversation
    history = get_chat_history(
        db=db,
        user_id=current_user.id,
        limit=10
    )

    conversation = ""

    for msg in history:
        conversation += f"{msg.role}: {msg.message}\n"

    # Run AI Agent
    result = run_agent(
        message=request.message,
        history=conversation
    )

    # Save assistant response
    save_message(
        db=db,
        user_id=current_user.id,
        role="assistant",
        message=result["answer"]
    )

    return {
        "response": result["answer"],
        "sources": result.get("sources", [])
    }