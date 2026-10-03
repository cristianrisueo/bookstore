# Punto de entrada de la aplicación FastAPI.
import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.authors.router import router as authors_router
from bookstore.books.router import router as books_router
from bookstore.core.config import get_settings
from bookstore.core.database import create_engine, create_session_factory, get_session
from bookstore.core.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Ciclo de vida de la app: lo anterior al yield se ejecuta al arrancar y lo posterior al apagar.
    Al arrancar: lee la configuración (si falta DATABASE_URL, la app no arranca) y crea el pool.
    Al apagar: cierra las conexiones del pool de forma ordenada.
    """
    engine = create_engine(get_settings())
    app.state.session_factory = create_session_factory(engine)

    try:
        yield
    finally:
        await engine.dispose()


# Crea la aplicación de FastAPI
app = FastAPI(title="Bookstore", lifespan=lifespan)

# Registra los manejadores de excepciones para traducir errores de dominio a respuestas HTTP
register_exception_handlers(app)

# Crea un router para la API de libros, autores y los incluye en la aplicación
app.include_router(books_router)
app.include_router(authors_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """
    Liveness: el proceso está vivo. No toca la base de datos a propósito: si un orquestador reinicia la API
    cuando esto falla, una caída de Postgres provocaría reinicios en cadena que no arreglan nada.
    """
    return {"status": "ok"}


@app.get("/health/ready", responses={503: {"description": "La base de datos no responde"}})
async def ready(session: Annotated[AsyncSession, Depends(get_session)]) -> dict[str, str]:
    """Readiness: la API puede atender peticiones porque llega a la base de datos. Si no, 503."""
    try:
        async with asyncio.timeout(2):
            await session.execute(text("SELECT 1"))
    # OSError cubre la conexión rechazada (asyncpg no siempre la envuelve) y TimeoutError
    except (SQLAlchemyError, OSError) as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Database unavailable") from exc
    return {"status": "ok"}
