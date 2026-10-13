from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.chat import router as chat_router
from app.routers.documents import router as document_router
from app.routers.business_datasets import router as business_datasets_router


app = FastAPI(
    title="AI Business OS",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(document_router)
app.include_router(business_datasets_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI Business OS Backend Running 🚀"
    }