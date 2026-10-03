# Reglas de validación de los schemas de entrada. Lógica pura: sin base de datos ni HTTP.
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from bookstore.authors.schemas import AuthorIn
from bookstore.books.schemas import BookIn

LIBRO = {"title": "Dune", "author_id": 1, "pages": 412}


@pytest.mark.parametrize(
    ("schema", "datos"),
    [
        (AuthorIn, {"name": ""}),
        (AuthorIn, {"name": "   "}),  # se recortan los espacios antes de comprobar la longitud mínima
        (AuthorIn, {"name": "x" * 256}),  # la columna es String(255)
        (AuthorIn, {"name": "Frank Herbert", "edad": 65}),
        (BookIn, {**LIBRO, "title": "   "}),
        (BookIn, {**LIBRO, "title": "x" * 256}),
        (BookIn, {**LIBRO, "pages": 0}),
        (BookIn, {**LIBRO, "author_id": 0}),
        (BookIn, {**LIBRO, "isbn": "978-0441013593"}),
    ],
    ids=[
        "autor-vacio",
        "autor-solo-espacios",
        "autor-256",
        "autor-campo-extra",
        "titulo-solo-espacios",
        "titulo-256",
        "paginas-cero",
        "autor-id-cero",
        "libro-campo-extra",
    ],
)
def test_schemas_rechazan_entradas_invalidas(schema: type[BaseModel], datos: dict[str, Any]) -> None:
    """Cada entrada viola una sola regla del contrato y debe rechazarse."""
    with pytest.raises(ValidationError):
        schema.model_validate(datos)
