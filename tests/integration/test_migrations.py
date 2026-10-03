# Migraciones de Alembic. Cada test trabaja en su propia base de datos vacía (bd_migraciones).
import subprocess
from collections.abc import Callable
from typing import Any

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# La fixture alembic del conftest: alembic(url, *argumentos)
type AlembicRunner = Callable[..., None]


def test_modelos_y_migraciones_coinciden(bd_migraciones: str, alembic: AlembicRunner) -> None:
    """
    Tras aplicar todas las migraciones, alembic check no detecta diferencias con los modelos.
    Caza una migración olvidada después de tocar un modelo. Ojo: no compara los CHECK.
    """
    alembic(bd_migraciones, "upgrade", "head")
    alembic(bd_migraciones, "check")


def test_migraciones_bajan_y_suben_en_vacio(bd_migraciones: str, alembic: AlembicRunner) -> None:
    """Todas las migraciones se pueden deshacer y volver a aplicar: caza downgrades rotos."""
    alembic(bd_migraciones, "upgrade", "head")
    alembic(bd_migraciones, "downgrade", "base")
    alembic(bd_migraciones, "upgrade", "head")


# TDD en rojo: hoy la migración añade author_id NOT NULL sin rellenarlo y falla con libros existentes
@pytest.mark.xfail(strict=True, raises=subprocess.CalledProcessError, reason="b4a93e7c8ffd no rellena author_id")
async def test_relacionar_books_con_authors_conserva_datos(bd_migraciones: str, alembic: AlembicRunner) -> None:
    """
    La migración que sustituye books.author (texto) por author_id (FK) conserva los datos al subir y al bajar,
    como pasaría al desplegarla sobre una base con libros y al hacer rollback.
    """
    alembic(bd_migraciones, "upgrade", "da16cffb9d8d")
    await ejecutar(
        bd_migraciones,
        "INSERT INTO books (title, author, pages) VALUES "
        "('Dune', 'Frank Herbert', 412), ('Hijos de Dune', 'Frank Herbert', 444), ('Fundación', 'Isaac Asimov', 255)",
    )

    # Subida: un autor por nombre distinto, y cada libro apunta al suyo
    alembic(bd_migraciones, "upgrade", "head")
    assert await consultar(bd_migraciones, "SELECT name FROM authors ORDER BY name") == [
        ("Frank Herbert",),
        ("Isaac Asimov",),
    ]
    assert await consultar(
        bd_migraciones, "SELECT b.title, a.name FROM books b JOIN authors a ON a.id = b.author_id ORDER BY b.title"
    ) == [("Dune", "Frank Herbert"), ("Fundación", "Isaac Asimov"), ("Hijos de Dune", "Frank Herbert")]

    # Bajada: cada libro recupera el nombre de su autor como texto
    alembic(bd_migraciones, "downgrade", "-1")
    assert await consultar(bd_migraciones, "SELECT title, author FROM books ORDER BY title") == [
        ("Dune", "Frank Herbert"),
        ("Fundación", "Isaac Asimov"),
        ("Hijos de Dune", "Frank Herbert"),
    ]

    # Y se puede volver a subir sobre esos datos
    alembic(bd_migraciones, "upgrade", "head")


async def ejecutar(url: str, sql: str) -> None:
    """Ejecuta SQL crudo y confirma. Crudo porque en revisiones intermedias los modelos no casan con el esquema."""
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.execute(text(sql))
    await engine.dispose()


async def consultar(url: str, sql: str) -> list[tuple[Any, ...]]:
    """Devuelve las filas de una consulta como tuplas."""
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        filas = [tuple(fila) for fila in await conn.execute(text(sql))]
    await engine.dispose()
    return filas
