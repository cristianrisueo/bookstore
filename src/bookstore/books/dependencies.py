# Construye las dependencias de la capa de libros. Se usa en las rutas para inyectar el servicio.
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.authors.dependencies import AuthorServiceDep
from bookstore.books.repository import BookRepository, SqlBookRepository
from bookstore.books.service import BookService
from bookstore.core.database import get_session


def get_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> BookRepository:
    """Construye el repositorio con la sesión de la petición actual."""
    return SqlBookRepository(session)


def get_service(
    repository: Annotated[BookRepository, Depends(get_repository)],
    author_service: AuthorServiceDep,
) -> BookService:
    """Construye el servicio de libros con su repositorio y el servicio de autores."""
    return BookService(repository, author_service)


# Atajo para reutilizar en las rutas: inyecta el servicio de libros ya construido
BookServiceDep = Annotated[BookService, Depends(get_service)]
