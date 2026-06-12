from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

# Импортируем модели из models
from ..schemas.crm import (
    CalculationLink,
    ClientCreate,
    ClientUpdate,
    NoteCreate,
    SessionCreate,
)


def create_client(db: Session, client_data: ClientCreate) -> Dict[str, Any]:
    """
    Создать нового клиента.

    Args:
        db: Сессия базы данных
        client_data: Данные клиента

    Returns:
        Словарь с данными созданного клиента
    """
    # SQL запрос для вставки данных клиента
    query = """
    INSERT INTO t_crm_client 
    (name, email, phone, birth_date, birth_time, notes, created_at, updated_at)
    VALUES 
    (:name, :email, :phone, :birth_date, :birth_time, :notes, NOW(), NOW())
    RETURNING id, name, email, phone, birth_date, birth_time, notes, created_at, updated_at
    """

    # Выполняем SQL запрос напрямую
    result = db.execute(text(query),
        {
            "name": client_data.name,
            "email": client_data.email,
            "phone": client_data.phone,
            "birth_date": client_data.birth_date,
            "birth_time": client_data.birth_time,
            "notes": client_data.notes,
        },
    ).fetchone()

    db.commit()

    # Преобразуем результат в словарь
    client = {
        "id": result.id,
        "name": result.name,
        "email": result.email,
        "phone": result.phone,
        "birth_date": result.birth_date,
        "birth_time": result.birth_time,
        "notes": result.notes,
        "created_at": result.created_at,
        "updated_at": result.updated_at,
    }

    return client


def list_clients(
    db: Session, search: Optional[str] = None, limit: int = 100, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Получить список клиентов с возможностью поиска.

    Args:
        db: Сессия базы данных
        search: Поисковый запрос
        limit: Максимальное количество результатов
        offset: Смещение для пагинации

    Returns:
        Список словарей с данными клиентов
    """
    # Базовый SQL запрос
    query = """
    SELECT 
        id, name, email, phone, birth_date, birth_time, notes, created_at, updated_at
    FROM 
        t_crm_client
    """

    # Добавляем условие поиска, если оно задано
    params = {}
    if search:
        query += """
        WHERE 
            name ILIKE :search 
            OR email ILIKE :search 
            OR phone ILIKE :search
        """
        params["search"] = f"%{search}%"

    # Добавляем сортировку, лимит и смещение
    query += """
    ORDER BY
        name
    LIMIT :limit OFFSET :offset
    """
    params["limit"] = limit
    params["offset"] = offset

    # Выполняем SQL запрос напрямую
    results = db.execute(text(query), params).fetchall()

    # Преобразуем результаты в список словарей
    clients = []
    for row in results:
        client = {
            "id": row.id,
            "name": row.name,
            "email": row.email,
            "phone": row.phone,
            "birth_date": row.birth_date,
            "birth_time": row.birth_time,
            "notes": row.notes,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
        clients.append(client)

    return clients


def get_client(db: Session, client_id: int) -> Dict[str, Any]:
    """
    Получить данные клиента по ID.

    Args:
        db: Сессия базы данных
        client_id: ID клиента

    Returns:
        Словарь с данными клиента
    """
    # SQL запрос для получения данных клиента
    query = """
    SELECT 
        id, name, email, phone, birth_date, birth_time, notes, created_at, updated_at
    FROM 
        t_crm_client
    WHERE 
        id = :client_id
    """

    # Выполняем SQL запрос напрямую
    result = db.execute(text(query), {"client_id": client_id}).fetchone()

    if not result:
        return None

    # Преобразуем результат в словарь
    client = {
        "id": result.id,
        "name": result.name,
        "email": result.email,
        "phone": result.phone,
        "birth_date": result.birth_date,
        "birth_time": result.birth_time,
        "notes": result.notes,
        "created_at": result.created_at,
        "updated_at": result.updated_at,
    }

    return client


def update_client(
    db: Session, client_id: int, client_data: ClientUpdate
) -> Dict[str, Any]:
    """
    Обновить данные клиента.

    Args:
        db: Сессия базы данных
        client_id: ID клиента
        client_data: Данные для обновления

    Returns:
        Словарь с обновленными данными клиента
    """
    # Проверяем, что клиент существует
    client = get_client(db, client_id)
    if not client:
        return None

    # Формируем SQL запрос для обновления данных
    # Обновляем только те поля, которые были переданы в client_data
    update_parts = []
    params = {"client_id": client_id}

    if client_data.name is not None:
        update_parts.append("name = :name")
        params["name"] = client_data.name

    if client_data.email is not None:
        update_parts.append("email = :email")
        params["email"] = client_data.email

    if client_data.phone is not None:
        update_parts.append("phone = :phone")
        params["phone"] = client_data.phone

    if client_data.birth_date is not None:
        update_parts.append("birth_date = :birth_date")
        params["birth_date"] = client_data.birth_date

    if client_data.birth_time is not None:
        update_parts.append("birth_time = :birth_time")
        params["birth_time"] = client_data.birth_time

    if client_data.notes is not None:
        update_parts.append("notes = :notes")
        params["notes"] = client_data.notes

    # Добавляем обновление updated_at
    update_parts.append("updated_at = NOW()")

    # Если нет полей для обновления, просто возвращаем текущие данные
    if not update_parts:
        return client

    # Whitelist для колонок (защита от SQL-инъекции через имена колонок)
    ALLOWED_COLUMNS = {"name", "email", "phone", "birth_date", "birth_time", "notes"}
    for part in update_parts:
        col_name = part.split("=")[0].strip()
        if col_name not in ALLOWED_COLUMNS:
            raise ValueError(f"Недопустимая колонка для обновления: {col_name}")

    # Формируем и выполняем SQL запрос
    query = f"""
    UPDATE t_crm_client
    SET {", ".join(update_parts)}
    WHERE id = :client_id
    RETURNING id, name, email, phone, birth_date, birth_time, notes, created_at, updated_at
    """

    # Выполняем SQL запрос напрямую
    result = db.execute(text(query), params).fetchone()

    db.commit()

    # Преобразуем результат в словарь
    updated_client = {
        "id": result.id,
        "name": result.name,
        "email": result.email,
        "phone": result.phone,
        "birth_date": result.birth_date,
        "birth_time": result.birth_time,
        "notes": result.notes,
        "created_at": result.created_at,
        "updated_at": result.updated_at,
    }

    return updated_client


def delete_client(db: Session, client_id: int) -> bool:
    """
    Удалить клиента.

    Args:
        db: Сессия базы данных
        client_id: ID клиента

    Returns:
        True, если клиент успешно удален, иначе False
    """
    # Проверяем, что клиент существует
    client = get_client(db, client_id)
    if not client:
        return False

    # SQL запрос для удаления клиента
    query = """
    DELETE FROM t_crm_client
    WHERE id = :client_id
    """

    # Выполняем SQL запрос напрямую
    db.execute(text(query), {"client_id": client_id})

    db.commit()

    return True


def create_session(db: Session, session_data: SessionCreate) -> Dict[str, Any]:
    """
    Создать новую сессию для клиента.

    Args:
        db: Сессия базы данных
        session_data: Данные сессии

    Returns:
        Словарь с данными созданной сессии

    Raises:
        ValueError: Если клиент не найден
    """
    # Проверяем существование клиента
    client = get_client(db, session_data.client_id)
    if not client:
        raise ValueError(f"Клиент с ID {session_data.client_id} не найден")

    # SQL запрос для вставки данных сессии
    query = """
    INSERT INTO t_crm_session 
    (client_id, date, notes, summary, created_at)
    VALUES 
    (:client_id, :date, :notes, :summary, NOW())
    RETURNING id, client_id, date, notes, summary, created_at
    """

    # Выполняем SQL запрос напрямую
    result = db.execute(text(query),
        {
            "client_id": session_data.client_id,
            "date": session_data.date,
            "notes": session_data.notes,
            "summary": session_data.summary,
        },
    ).fetchone()

    db.commit()

    # Преобразуем результат в словарь
    session = {
        "id": result.id,
        "client_id": result.client_id,
        "date": result.date,
        "notes": result.notes,
        "summary": result.summary,
        "created_at": result.created_at,
    }

    return session


def list_client_sessions(
    db: Session, client_id: int, limit: int = 100, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Получить список сессий клиента с пагинацией.

    Args:
        db: Сессия базы данных
        client_id: ID клиента
        limit: Максимальное количество результатов
        offset: Смещение для пагинации

    Returns:
        Список словарей с данными сессий
    """
    query = """
    SELECT 
        id, client_id, date, notes, summary, created_at
    FROM 
        t_crm_session
    WHERE 
        client_id = :client_id
    ORDER BY
        date DESC
    LIMIT :limit OFFSET :offset
    """

    results = db.execute(text(query), {"client_id": client_id, "limit": limit, "offset": offset}
    ).fetchall()

    # Преобразуем результаты в список словарей
    sessions = []
    for row in results:
        session = {
            "id": row.id,
            "client_id": row.client_id,
            "date": row.date,
            "notes": row.notes,
            "summary": row.summary,
            "created_at": row.created_at,
        }
        sessions.append(session)

    return sessions


def link_calculation(db: Session, link_data: CalculationLink) -> Dict[str, Any]:
    """
    Привязать расчет к клиенту.

    Args:
        db: Сессия базы данных
        link_data: Данные связи

    Returns:
        Словарь с данными созданной связи

    Raises:
        ValueError: Если клиент не найден
    """
    # Проверяем существование клиента
    client = get_client(db, link_data.client_id)
    if not client:
        raise ValueError(f"Клиент с ID {link_data.client_id} не найден")

    # SQL запрос для вставки данных связи
    query = """
    INSERT INTO t_crm_calculation 
    (client_id, calculation_type, reference_id, notes, created_at)
    VALUES 
    (:client_id, :calculation_type, :reference_id, :notes, NOW())
    RETURNING id, client_id, calculation_type, reference_id, notes, created_at
    """

    # Выполняем SQL запрос напрямую
    result = db.execute(text(query),
        {
            "client_id": link_data.client_id,
            "calculation_type": link_data.calculation_type,
            "reference_id": link_data.reference_id,
            "notes": link_data.notes,
        },
    ).fetchone()

    db.commit()

    # Преобразуем результат в словарь
    calculation_link = {
        "id": result.id,
        "client_id": result.client_id,
        "calculation_type": result.calculation_type,
        "reference_id": result.reference_id,
        "notes": result.notes,
        "created_at": result.created_at,
    }

    return calculation_link


def get_client_calculations(
    db: Session,
    client_id: int,
    calculation_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Получить список расчетов, привязанных к клиенту, с пагинацией.

    Args:
        db: Сессия базы данных
        client_id: ID клиента
        calculation_type: Тип расчета (tongshu, qimen, etc.)
        limit: Максимальное количество результатов
        offset: Смещение для пагинации

    Returns:
        Список словарей с данными связей
    """
    query = """
    SELECT 
        id, client_id, calculation_type, reference_id, notes, created_at
    FROM 
        t_crm_calculation
    WHERE 
        client_id = :client_id
    """

    params = {"client_id": client_id}
    if calculation_type:
        query += " AND calculation_type = :calculation_type"
        params["calculation_type"] = calculation_type

    query += """
    ORDER BY
        created_at DESC
    LIMIT :limit OFFSET :offset
    """
    params["limit"] = limit
    params["offset"] = offset

    results = db.execute(text(query), params).fetchall()

    # Преобразуем результаты в список словарей
    calculations = []
    for row in results:
        calculation = {
            "id": row.id,
            "client_id": row.client_id,
            "calculation_type": row.calculation_type,
            "reference_id": row.reference_id,
            "notes": row.notes,
            "created_at": row.created_at,
        }
        calculations.append(calculation)

    return calculations


def create_note(db: Session, note_data: NoteCreate) -> Dict[str, Any]:
    """
    Создать новую заметку для клиента.

    Args:
        db: Сессия базы данных
        note_data: Данные заметки

    Returns:
        Словарь с данными созданной заметки

    Raises:
        ValueError: Если клиент не найден
    """
    # Проверяем существование клиента
    client = get_client(db, note_data.client_id)
    if not client:
        raise ValueError(f"Клиент с ID {note_data.client_id} не найден")

    # SQL запрос для вставки данных заметки
    query = """
    INSERT INTO t_crm_note 
    (client_id, note_text, calculation_id, created_at)
    VALUES 
    (:client_id, :note_text, :calculation_id, NOW())
    RETURNING id, client_id, note_text, calculation_id, created_at
    """

    # Выполняем SQL запрос напрямую
    result = db.execute(text(query),
        {
            "client_id": note_data.client_id,
            "note_text": note_data.note_text,
            "calculation_id": note_data.calculation_id,
        },
    ).fetchone()

    db.commit()

    # Преобразуем результат в словарь
    note = {
        "id": result.id,
        "client_id": result.client_id,
        "note_text": result.note_text,
        "calculation_id": result.calculation_id,
        "created_at": result.created_at,
    }

    return note


def get_client_notes(
    db: Session, client_id: int, limit: int = 100, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Получить список заметок для клиента с пагинацией.

    Args:
        db: Сессия базы данных
        client_id: ID клиента
        limit: Максимальное количество результатов
        offset: Смещение для пагинации

    Returns:
        Список словарей с данными заметок
    """
    query = """
    SELECT 
        id, client_id, note_text, calculation_id, created_at
    FROM 
        t_crm_note
    WHERE 
        client_id = :client_id
    ORDER BY
        created_at DESC
    LIMIT :limit OFFSET :offset
    """

    results = db.execute(text(query), {"client_id": client_id, "limit": limit, "offset": offset}
    ).fetchall()

    # Преобразуем результаты в список словарей
    notes = []
    for row in results:
        note = {
            "id": row.id,
            "client_id": row.client_id,
            "note_text": row.note_text,
            "calculation_id": row.calculation_id,
            "created_at": row.created_at,
        }
        notes.append(note)

    return notes
