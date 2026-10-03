# Integridad de la tabla books, llamando al repositorio directamente.
# Son casos inalcanzables por HTTP: Pydantic y el servicio los filtran antes de llegar a la base de datos.
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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
    IntegrityError sin traducir: es la guarda de que solo se traduce la FK de autor.
    """
    autor = await SqlAuthorRepository(session).add(AuthorIn(name="Frank Herbert"))
    # model_construct se salta la validación de Pydantic, que rechazaría pages=0 antes de llegar a la BD
    libro = BookIn.model_construct(title="Dune", author_id=autor.id, pages=0)

    with pytest.raises(IntegrityError) as error:
        await SqlBookRepository(session).add(libro)

    original = error.value.orig  # error del driver (asyncpg) que SQLAlchemy envuelve
    assert getattr(original, "sqlstate", None) == CHECK_VIOLATION
    assert getattr(original and original.__cause__, "constraint_name", None) == "ck_books_pages_positive"
    await session.rollback()
    assert await session.scalar(select(func.count()).select_from(BookModel)) == 0
