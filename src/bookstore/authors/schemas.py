# Modelos de datos para la API de autores
from pydantic import BaseModel, ConfigDict, Field


class AuthorIn(BaseModel):
    """Datos necesarios para crear un autor."""

    # Quita espacios sobrantes y rechaza campos que no existen en el modelo
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    # No se admiten nombres vacíos, y el nombre no puede superar los 255 caracteres.
    name: str = Field(min_length=1, max_length=255, description="Nombre del autor", examples=["Frank Herbert"])


class Author(BaseModel):
    """Autor almacenado, con el identificador asignado por la base de datos."""

    id: int
    name: str
