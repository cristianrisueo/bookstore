# Contrato HTTP de autores contra PostgreSQL real.
from httpx import AsyncClient


async def test_crear_y_obtener_autor(client: AsyncClient) -> None:
    """POST devuelve 201 con el autor y su id; el GET (otra sesión) lo lee de la BD, con el nombre sin espacios."""
    creado = await client.post("/authors", json={"name": "  Frank Herbert  "})

    assert creado.status_code == 201
    autor = creado.json()
    assert autor == {"id": autor["id"], "name": "Frank Herbert"}

    leido = await client.get(f"/authors/{autor['id']}")

    assert leido.status_code == 200
    assert leido.json() == autor


async def test_obtener_autor_inexistente_devuelve_404(client: AsyncClient) -> None:
    """AuthorNotFoundError se traduce a 404 con un detail legible."""
    respuesta = await client.get("/authors/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Author 999 not found"}
