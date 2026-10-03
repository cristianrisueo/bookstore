# Modelos de datos para la base de datos de libros.
# Son clases de SQLAlchemy: describen cómo se guardan los datos, no lo que ve la API
from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bookstore.authors.models import AuthorModel
from bookstore.core.database import Base


class BookModel(Base):
    """
    Clase que representa un libro en la base de datos.
    Hereda de Base, que es la clase de SQLAlchemy para todas las tablas.
    """

    # Nombre de la tabla en Postgres
    __tablename__ = "books"

    # Restricción en la tabla: pages es un número positivo.
    # Pydantic ya lo valida en la API, pero así la tabla se protege aunque alguien
    # escriba en ella por otro camino (un script, una migración, otro servicio)
    __table_args__ = (CheckConstraint("pages > 0", name="ck_books_pages_positive"),)

    # Columnas de la tabla.
    id: Mapped[int] = mapped_column(primary_key=True)  # Int, clave primaria, autoincremental
    title: Mapped[str] = mapped_column(String(255))  # String de hasta 255 caracteres, NOT NULL
    pages: Mapped[int] = mapped_column()  # Int, NOT NULL, sin más opciones
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), index=True)  # FK hacia authors.id

    # Relación con la tabla de autores. SQLAlchemy puede cargar el autor de un libro cuando haga falta.
    # lazy="raise" significa que si alguien intenta acceder a book.author y no se ha cargado, SQLAlchemy lanza un error.
    author: Mapped[AuthorModel] = relationship(lazy="raise")
