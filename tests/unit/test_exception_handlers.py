# Traducción de errores de dominio a HTTP. Solo el 409: ningún endpoint lanza aún un ConflictError,
# así que este es el único nivel donde se puede probar. El 404 ya lo cubren los tests de integración.
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from bookstore.core.exception_handlers import register_exception_handlers
from bookstore.core.exceptions import ConflictError


class DuplicadoError(ConflictError):
    """Error de un dominio inventado: comprueba que la traducción funciona por herencia."""


async def test_conflict_error_se_traduce_a_409() -> None:
    """Cualquier subclase de ConflictError llega al cliente como 409 con su mensaje en detail."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/conflicto")
    async def conflicto() -> None:
        raise DuplicadoError("Ya existe")

    # La app corre en memoria, dentro del mismo proceso: no hay red ni base de datos
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        respuesta = await client.get("/conflicto")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "Ya existe"}
