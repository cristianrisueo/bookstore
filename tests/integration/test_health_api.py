# Readiness: comprueba de verdad la conexión con la base de datos.
from collections.abc import AsyncIterator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.core.config import Settings
from bookstore.core.database import create_engine, create_session_factory, get_session
from bookstore.main import app

# Nada escucha en el puerto 1: la conexión se rechaza de verdad, sin dobles ni parar contenedores
URL_INALCANZABLE = "postgresql+asyncpg://x:x@127.0.0.1:1/x"


async def test_ready_devuelve_200_con_bd(client: AsyncClient) -> None:
    """Con Postgres disponible, readiness ejecuta SELECT 1 y responde 200."""
    respuesta = await client.get("/health/ready")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


async def test_ready_devuelve_503_sin_bd(client: AsyncClient) -> None:
    """Si la base de datos no responde, readiness da 503: ni se traga el error (200) ni lo deja escapar (500)."""
    engine = create_engine(Settings(database_url=URL_INALCANZABLE, _env_file=None))
    session_factory = create_session_factory(engine)

    async def session_sin_bd() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    # Sustituye la sesión que puso la fixture client; la fixture retira la sustitución al terminar
    app.dependency_overrides[get_session] = session_sin_bd
    try:
        respuesta = await client.get("/health/ready")
    finally:
        await engine.dispose()

    assert respuesta.status_code == 503
    assert respuesta.json() == {"detail": "Database unavailable"}
