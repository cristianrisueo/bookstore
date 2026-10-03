# Construye las dependencias de la capa de autores. Se usa en las rutas para inyectar el servicio.
# También lo usará el dominio de libros para comprobar que el autor de un libro existe.
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.authors.repository import AuthorRepository, SqlAuthorRepository
from bookstore.authors.service import AuthorService
from bookstore.core.database import get_session


def get_author_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthorRepository:
    """Construye el repositorio con la sesión de la petición actual."""
    return SqlAuthorRepository(session)


def get_author_service(
    repository: Annotated[AuthorRepository, Depends(get_author_repository)],
) -> AuthorService:
    """Construye el servicio con el repositorio ya resuelto."""
    return AuthorService(repository)


# Atajo para reutilizar en las rutas: inyecta el servicio de autores ya construido
AuthorServiceDep = Annotated[AuthorService, Depends(get_author_service)]
