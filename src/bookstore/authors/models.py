# Modelos de datos para la base de datos de autores.
# Son clases de SQLAlchemy: describen cómo se guardan los datos, no lo que ve la API
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from bookstore.core.database import Base


class AuthorModel(Base):
    """
    Clase que representa un autor en la base de datos.
    Hereda de Base, que es la clase de SQLAlchemy para todas las tablas.
    """

    # Nombre de la tabla en Postgres
    __tablename__ = "authors"

    # Columnas de la tabla.
    id: Mapped[int] = mapped_column(primary_key=True)  # Int, clave primaria, autoincremental
    name: Mapped[str] = mapped_column(String(255))  # String de hasta 255 caracteres, NOT NULL
