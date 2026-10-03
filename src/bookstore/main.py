# Punto de entrada de la aplicación FastAPI.
from fastapi import FastAPI

from bookstore.authors.router import router as authors_router
from bookstore.books.router import router as books_router
from bookstore.core.exception_handlers import register_exception_handlers

# Crea la aplicación de FastAPI
app = FastAPI(title="Bookstore")

# Registra los manejadores de excepciones para traducir errores de dominio a respuestas HTTP
register_exception_handlers(app)

# Crea un router para la API de libros, autores y los incluye en la aplicación
app.include_router(books_router)
app.include_router(authors_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Endpoint de salud para comprobar que la API está funcionando."""
    return {"status": "ok"}
