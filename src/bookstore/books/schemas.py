# Modelos de datos para la API de libros.
from pydantic import BaseModel, ConfigDict, Field

from bookstore.authors.schemas import Author


class BookIn(BaseModel):
    """Datos necesarios para crear un libro."""

    # Quita espacios sobrantes y rechaza campos que no existen en el modelo
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    # No se admiten títulos ni autores vacíos, y el número de páginas debe ser mayor que 0.
    title: str = Field(min_length=1, max_length=255, description="Título del libro", examples=["Dune"])
    author_id: int = Field(gt=0, description="Identificador de un autor existente", examples=[1])
    pages: int = Field(gt=0, description="Número de páginas", examples=[412])


class Book(BaseModel):
    """Libro almacenado, con el autor asociado anidado."""

    id: int
    title: str
    pages: int
    author: Author
