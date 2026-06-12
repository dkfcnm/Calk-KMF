from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..schemas.crm import (
    CalculationLink,
    Client,
    ClientCreate,
    ClientUpdate,
    Note,
    NoteCreate,
    Session,
    SessionCreate,
)
from ..services import crm_service

router = APIRouter()


# Маршруты API


# Клиенты
@router.post("/clients/", response_model=Client)
def create_client(
    client_data: ClientCreate = Body(...), db: Session = Depends(get_db)
):
    """
    Создать нового клиента.
    """
    try:
        client = crm_service.create_client(db, client_data)
        return client
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка создания клиента: {str(e)}"
        )


@router.get("/clients/", response_model=List[Client])
def list_clients(
    search: Optional[str] = Query(
        None, description="Поиск по имени, email или телефону"
    ),
    limit: int = Query(100, description="Максимальное количество результатов"),
    offset: int = Query(0, description="Смещение для пагинации"),
    db: Session = Depends(get_db),
):
    """
    Получить список клиентов с возможностью поиска.
    """
    try:
        clients = crm_service.list_clients(db, search, limit, offset)
        return clients
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения списка клиентов: {str(e)}"
        )


@router.get("/clients/{client_id}", response_model=Client)
def get_client(
    client_id: int = Path(..., description="ID клиента"), db: Session = Depends(get_db)
):
    """
    Получить данные клиента по ID.
    """
    try:
        client = crm_service.get_client(db, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Клиент не найден")
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения данных клиента: {str(e)}"
        )


@router.put("/clients/{client_id}", response_model=Client)
def update_client(
    client_id: int = Path(..., description="ID клиента"),
    client_data: ClientUpdate = Body(...),
    db: Session = Depends(get_db),
):
    """
    Обновить данные клиента.
    """
    try:
        updated_client = crm_service.update_client(db, client_id, client_data)
        if not updated_client:
            raise HTTPException(status_code=404, detail="Клиент не найден")
        return updated_client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка обновления данных клиента: {str(e)}"
        )


@router.delete("/clients/{client_id}", response_model=dict)
def delete_client(
    client_id: int = Path(..., description="ID клиента"), db: Session = Depends(get_db)
):
    """
    Удалить клиента.
    """
    try:
        success = crm_service.delete_client(db, client_id)
        if not success:
            raise HTTPException(status_code=404, detail="Клиент не найден")
        return {"success": True, "message": "Клиент успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка удаления клиента: {str(e)}"
        )


# Сессии
@router.post("/sessions/", response_model=Session)
def create_session(
    session_data: SessionCreate = Body(...), db: Session = Depends(get_db)
):
    """
    Создать новую сессию для клиента.
    """
    try:
        session = crm_service.create_session(db, session_data)
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания сессии: {str(e)}")


@router.get("/clients/{client_id}/sessions", response_model=List[Session])
def list_client_sessions(
    client_id: int = Path(..., description="ID клиента"), db: Session = Depends(get_db)
):
    """
    Получить список сессий клиента.
    """
    try:
        sessions = crm_service.list_client_sessions(db, client_id)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения списка сессий: {str(e)}"
        )


# Расчеты
@router.post("/calculations/link", response_model=CalculationLink)
def link_calculation(
    link_data: CalculationLink = Body(...), db: Session = Depends(get_db)
):
    """
    Привязать расчет к клиенту.
    """
    try:
        calculation_link = crm_service.link_calculation(db, link_data)
        return calculation_link
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка привязки расчета: {str(e)}"
        )


@router.get("/clients/{client_id}/calculations", response_model=List[CalculationLink])
def get_client_calculations(
    client_id: int = Path(..., description="ID клиента"),
    calculation_type: Optional[str] = Query(
        None, description="Тип расчета (tongshu, qimen, etc.)"
    ),
    db: Session = Depends(get_db),
):
    """
    Получить список расчетов, привязанных к клиенту.
    """
    try:
        # Проверка существования клиента
        client = crm_service.get_client(db, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Клиент не найден")

        calculations = crm_service.get_client_calculations(
            db, client_id, calculation_type
        )
        return calculations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения расчетов: {str(e)}"
        )


# Заметки
@router.post("/notes/", response_model=Note)
def create_note(note_data: NoteCreate = Body(...), db: Session = Depends(get_db)):
    """
    Создать новую заметку для клиента.
    """
    try:
        note = crm_service.create_note(db, note_data)
        return note
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка создания заметки: {str(e)}"
        )


@router.get("/clients/{client_id}/notes", response_model=List[Note])
def get_client_notes(
    client_id: int = Path(..., description="ID клиента"), db: Session = Depends(get_db)
):
    """
    Получить список заметок для клиента.
    """
    try:
        notes = crm_service.get_client_notes(db, client_id)
        return notes
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения заметок: {str(e)}"
        )
