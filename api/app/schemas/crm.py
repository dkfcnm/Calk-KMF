from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class ClientBase(BaseModel):
    """Базовые данные клиента"""

    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    birth_time: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    """Данные для создания клиента"""

    pass


class ClientUpdate(ClientBase):
    """Данные для обновления клиента"""

    name: Optional[str] = None


class Client(ClientBase):
    """Полные данные клиента"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SessionBase(BaseModel):
    """Базовые данные сессии"""

    client_id: int
    date: date
    notes: Optional[str] = None
    summary: Optional[str] = None


class SessionCreate(SessionBase):
    """Данные для создания сессии"""

    pass


class Session(SessionBase):
    """Полные данные сессии"""

    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class CalculationLink(BaseModel):
    """Связь расчета с клиентом"""

    client_id: int
    calculation_type: str  # "tongshu", "qimen", etc.
    reference_id: str  # ID внешнего расчета
    notes: Optional[str] = None

    class Config:
        orm_mode = True


class NoteCreate(BaseModel):
    """Создание заметки"""

    client_id: int
    note_text: str
    calculation_id: Optional[str] = None


class Note(NoteCreate):
    """Полные данные заметки"""

    id: int
    created_at: datetime

    class Config:
        orm_mode = True
