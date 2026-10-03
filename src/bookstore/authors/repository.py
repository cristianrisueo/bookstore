# Repositorio de autores: Define la interfaz y su implementación sobre PostgreSQL.
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from bookstore.authors.models import AuthorModel
from bookstore.authors.schemas import Author, AuthorIn


class AuthorRepository(Protocol):
    """Interfaz de acceso a datos. Cualquier clase con estos métodos la cumple."""

    # Método para añadir un autor nuevo. Devuelve el id que le asigna la base de datos.
    async def add(self, data: AuthorIn) -> Author: ...

    # Método para buscar un autor por su id. Devuelve None si no existe.
    async def get(self, author_id: int) -> Author | None: ...


class SqlAuthorRepository:
    """Implementación sobre PostgreSQL con SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Recibe la sesión de SQLAlchemy que se usará para todas las operaciones."""
        self._session = session

    async def add(self, data: AuthorIn) -> Author:
        """Guarda un autor nuevo y lo devuelve con el id que le asigna Postgres."""

        # Crea un modelo de SQLAlchemy a partir del schema de Pydantic que viene de la API
        model = AuthorModel(name=data.name)

        # Lo apunta en la sesión y hace commit para que se guarde en la base de datos
        self._session.add(model)
        await self._session.commit()

        # Convierte el modelo de SQLAlchemy de vuelta a un schema de Pydantic para devolverlo
        return Author.model_validate(model, from_attributes=True)

    async def get(self, author_id: int) -> Author | None:
        """Busca un autor por su id. Devuelve None si no existe."""

        # Busca el modelo de SQLAlchemy en la base de datos por su id. Si no lo encuentra, None
        model = await self._session.get(AuthorModel, author_id)
        if model is None:
            return None

        # Convierte el modelo de SQLAlchemy a un schema de Pydantic para devolverlo
        return Author.model_validate(model, from_attributes=True)
