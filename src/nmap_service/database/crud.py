from typing import Generic, List, Optional, Type, TypeVar

from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def get(self, id: str) -> Optional[T]:
        return self.session.get(self.model, id)

    def get_all(self, offset: int = 0, limit: int = 100) -> List[T]:
        return self.session.exec(select(self.model).offset(offset).limit(limit)).all()

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True
