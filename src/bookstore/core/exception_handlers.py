# Manejo de excepciones para traducir errores a respuestas HTTP.
# Es el único sitio de la aplicación que decide qué código corresponde a cada error.
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from bookstore.core.exceptions import ConflictError, NotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    """Registra en la aplicación un manejador por cada familia de errores."""

    # Cualquier NotFoundError (o subclase, como BookNotFoundError) se convierte en un 404
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

    # Cualquier ConflictError (o subclase) se convierte en un 409
    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})
