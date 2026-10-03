# Cableado de la validación de entrada: un caso por endpoint. Las reglas en detalle se prueban en tests/unit.
from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    ("ruta", "cuerpo", "campo"),
    [
        ("/authors", {"name": "Frank Herbert", "edad": 65}, "edad"),
        ("/books", {"title": "Dune", "author_id": 1, "pages": 0}, "pages"),
    ],
    ids=["autor-campo-extra", "libro-paginas-cero"],
)
async def test_cuerpo_invalido_devuelve_422(client: AsyncClient, ruta: str, cuerpo: dict[str, Any], campo: str) -> None:
    """El router valida el cuerpo con el schema: 422 y el error señala el campo culpable."""
    respuesta = await client.post(ruta, json=cuerpo)

    assert respuesta.status_code == 422
    assert [error["loc"] for error in respuesta.json()["detail"]] == [["body", campo]]
