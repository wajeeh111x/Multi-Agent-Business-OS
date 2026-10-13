from app.database.database import Base, engine

from app.models.user import User
from app.models.chat import ChatMessage
from app.models.document import Document
from app.models.memory import Memory
from app.models.dataset import Dataset


Base.metadata.create_all(bind=engine)

print("Database created successfully!")