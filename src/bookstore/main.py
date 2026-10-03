# Punto de entrada de la aplicación FastAPI.
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from bookstore.authors.router import router as authors_router
from bookstore.books.router import router as books_router
from bookstore.core.config import get_settings
from bookstore.core.database import create_engine, create_session_factory
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
    """Endpoint de salud para comprobar que la API está funcionando."""
    return {"status": "ok"}
