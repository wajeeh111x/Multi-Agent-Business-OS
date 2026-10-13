from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), nullable=False)

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    # Existing relationship
    messages = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # NEW relationship
    memories = relationship(
        "Memory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    datasets = relationship(
        "Dataset",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    