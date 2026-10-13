from sqlalchemy.orm import Session

from app.models.memory import Memory


def save_memory(
    db: Session,
    user_id: int,
    category: str,
    memory: str
):
    new_memory = Memory(
        user_id=user_id,
        category=category,
        memory=memory
    )

    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)

    return new_memory


def get_memories(
    db: Session,
    user_id: int
):
    return (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .order_by(Memory.created_at.desc())
        .all()
    )


def search_memories(
    db: Session,
    user_id: int,
    keyword: str
):
    return (
        db.query(Memory)
        .filter(
            Memory.user_id == user_id,
            Memory.memory.ilike(f"%{keyword}%")
        )
        .all()
    )


def delete_memory(
    db: Session,
    memory_id: int
):
    memory = (
        db.query(Memory)
        .filter(Memory.id == memory_id)
        .first()
    )

    if memory:
        db.delete(memory)
        db.commit()

    return memory


def update_memory(
    db: Session,
    memory_id: int,
    new_memory: str
):
    memory = (
        db.query(Memory)
        .filter(Memory.id == memory_id)
        .first()
    )

    if memory:
        memory.memory = new_memory
        db.commit()
        db.refresh(memory)

    return memory