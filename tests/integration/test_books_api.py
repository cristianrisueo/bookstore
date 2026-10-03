# Contrato HTTP de libros contra PostgreSQL real.
from typing import Any

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bookstore.books.models import BookModel


async def crear_autor(client: AsyncClient, name: str = "Frank Herbert") -> dict[str, Any]:
    """Crea un autor por la API y devuelve su JSON."""
    respuesta = await client.post("/authors", json={"name": name})
    assert respuesta.status_code == 201
    autor: dict[str, Any] = respuesta.json()
    return autor


async def test_crear_y_obtener_libro(client: AsyncClient) -> None:
    """POST devuelve 201 con el autor anidado (no solo su id) y el GET devuelve exactamente lo mismo."""
    autor = await crear_autor(client)

    creado = await client.post("/books", json={"title": "Dune", "author_id": autor["id"], "pages": 412})

    assert creado.status_code == 201
    libro = creado.json()
    assert libro == {"id": libro["id"], "title": "Dune", "pages": 412, "author": autor}

    leido = await client.get(f"/books/{libro['id']}")

    assert leido.status_code == 200
    assert leido.json() == libro


async def test_obtener_libro_inexistente_devuelve_404(client: AsyncClient) -> None:
    """BookNotFoundError se traduce a 404 con un detail legible."""
    respuesta = await client.get("/books/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Book 999 not found"}


async def test_crear_libro_con_autor_inexistente_devuelve_404_y_no_inserta(
    client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """El servicio comprueba el autor antes de insertar: 404 y ninguna fila nueva en books."""
    respuesta = await client.post("/books", json={"title": "Dune", "author_id": 999, "pages": 412})

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Author 999 not found"}
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(BookModel)) == 0
