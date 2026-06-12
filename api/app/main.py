import logging
import traceback

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound

from .routers import bazi, crm, fengshui, profiles, qimen, refs, taiyi, tongshu

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Калькулятор китайской метафизики API",
    description="API для доступа к данным Тун Шу, Ци Мэнь и CRM-системы",
    version="1.0.0",
)


# Centralized exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Ошибка валидации данных", "errors": exc.errors()},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Database integrity error: {str(exc)}")
    return JSONResponse(
        status_code=409,
        content={"detail": "Конфликт данных. Возможно, запись уже существует."},
    )


@app.exception_handler(NoResultFound)
async def not_found_handler(request: Request, exc: NoResultFound):
    return JSONResponse(
        status_code=404,
        content={"detail": "Запрошенные данные не найдены."},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"Value error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже."},
    )


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на список разрешенных доменов
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(tongshu.router, prefix="/api/tongshu", tags=["Тун Шу"])
app.include_router(refs.router, prefix="/api/refs", tags=["Справочники"])
app.include_router(qimen.router, prefix="/api/qimen", tags=["Ци Мэнь"])
app.include_router(crm.router, prefix="/api/crm", tags=["CRM"])
app.include_router(bazi.router, prefix="/api/bazi", tags=["Ба Цзы"])
app.include_router(taiyi.router, prefix="/api/taiyi", tags=["Тай И"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["Профили"])
app.include_router(fengshui.router, prefix="/api/fengshui", tags=["Фэн Шуй / Летящие Звезды"])


# Корневой маршрут
@app.get("/")
async def root():
    return {
        "message": "Калькулятор китайской метафизики API",
        "version": "1.0.0",
        "documentation": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
