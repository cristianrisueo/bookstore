# Repositorio de libros: Define la interfaz y su implementación sobre PostgreSQL.
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bookstore.books.models import BookModel
from bookstore.books.schemas import Book, BookIn


class BookRepository(Protocol):
    """Interfaz de acceso a datos. Cualquier clase con estos métodos lo cumple."""

    # Método para añadir un libro nuevo. Devuelve el id que le asigna la base de datos.
    async def add(self, data: BookIn) -> Book: ...

    # Método para buscar un libro por su id. Devuelve None si no existe.
    async def get(self, book_id: int) -> Book | None: ...


class SqlBookRepository:
    """Implementación sobre PostgreSQL con SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Recibe la sesión de SQLAlchemy que se usará para todas las operaciones."""
        self._session = session

    async def add(self, data: BookIn) -> Book:
        """Guarda un libro nuevo y devuelve el id que le asigna Postgres."""

        # Crea un modelo de SQLAlchemy a partir del schema de Pydantic que viene de la API
        model = BookModel(title=data.title, author_id=data.author_id, pages=data.pages)

        # Lo apunta en la sesión y hace commit para que se guarde en la base de datos
        self._session.add(model)
        await self._session.commit()

        # Obtiene el libro recién creado, con el autor cargado, para devolverlo a la API
        book = await self.get(model.id)

        # Si por alguna razón no se encuentra el libro justo después de crearlo, lanza un error
        if book is None:
            raise RuntimeError(f"Book {model.id} not found right after creation")

        return book

    async def get(self, book_id: int) -> Book | None:
        """Busca un libro por su id. Devuelve None si no existe."""

        # Construye la consulta SQL para buscar el libro por id y cargar el autor anidado, no solo su id.
        stmt = select(BookModel).options(selectinload(BookModel.author)).where(BookModel.id == book_id)

        # Ejecuta la consulta y obtiene el modelo de SQLAlchemy, o None si no existe.
        model = await self._session.scalar(stmt)
        if model is None:
            return None

        # Convierte el modelo de SQLAlchemy a un schema de Pydantic para devolverlo
        return Book.model_validate(model, from_attributes=True)
