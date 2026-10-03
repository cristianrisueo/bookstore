# E2E: el flujo principal contra el sistema desplegado (imagen, lifespan, get_session real, red y migraciones).
# Los casos de error ya se prueban en integración; aquí solo el camino feliz.
import httpx


def test_flujo_crear_autor_libro_y_consultarlo(client: httpx.Client) -> None:
    """Crear un autor, crear un libro suyo y leerlo. Usa los ids devueltos: la base puede tener datos previos."""
    autor = client.post("/authors", json={"name": "Frank Herbert"})
    assert autor.status_code == 201

    libro = client.post("/books", json={"title": "Dune", "author_id": autor.json()["id"], "pages": 412})
    assert libro.status_code == 201
    assert libro.json()["author"] == autor.json()

    leido = client.get(f"/books/{libro.json()['id']}")
    assert leido.status_code == 200
    assert leido.json() == libro.json()
