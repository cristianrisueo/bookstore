# Integridad de la tabla books, llamando al repositorio directamente.
# Son casos inalcanzables por HTTP: Pydantic y el servicio los filtran antes de llegar a la base de datos.
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.authors.exceptions import AuthorNotFoundError
from bookstore.authors.repository import SqlAuthorRepository
from bookstore.authors.schemas import AuthorIn
from bookstore.books.models import BookModel
from bookstore.books.repository import SqlBookRepository
from bookstore.books.schemas import BookIn

# Códigos SQLSTATE de PostgreSQL
CHECK_VIOLATION = "23514"


async def test_check_rechaza_paginas_no_positivas(session: AsyncSession) -> None:
    """
    La migración creó el CHECK pages > 0 (alembic check no compara los CHECK), y su violación sale como
    IntegrityError sin traducir: es la guarda de que solo se traduce la FK de autor. Tras el error,
    la sesión sigue utilizable.
    """
    autor = await SqlAuthorRepository(session).add(AuthorIn(name="Frank Herbert"))
    # model_construct se salta la validación de Pydantic, que rechazaría pages=0 antes de llegar a la BD
    libro = BookIn.model_construct(title="Dune", author_id=autor.id, pages=0)

    with pytest.raises(IntegrityError) as error:
        await SqlBookRepository(session).add(libro)

    original = error.value.orig  # error del driver (asyncpg) que SQLAlchemy envuelve
    assert getattr(original, "sqlstate", None) == CHECK_VIOLATION
    assert getattr(original and original.__cause__, "constraint_name", None) == "ck_books_pages_positive"
    # La sesión sigue sirviendo tras el error (el repositorio hizo rollback) y no quedó nada a medias
    assert await session.scalar(select(func.count()).select_from(BookModel)) == 0


async def test_anadir_libro_con_autor_inexistente_lanza_author_not_found(session: AsyncSession) -> None:
    """
    Si el autor no existe (por ejemplo, se borró entre la comprobación del servicio y el insert), la FK
    salta y el repositorio la traduce a AuthorNotFoundError (404), no a un 500. Tras el error, la sesión
    sigue sirviendo: hubo rollback.
    """
    repositorio = SqlBookRepository(session)

    with pytest.raises(AuthorNotFoundError) as error:
        await repositorio.add(BookIn(title="Dune", author_id=999, pages=412))

    assert error.value.author_id == 999
    autor = await SqlAuthorRepository(session).add(AuthorIn(name="Frank Herbert"))
    libro = await repositorio.add(BookIn(title="Dune", author_id=autor.id, pages=412))
    assert await session.scalar(select(func.count()).select_from(BookModel)) == 1
    assert libro.author == autor
