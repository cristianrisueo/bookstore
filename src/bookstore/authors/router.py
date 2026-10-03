# Rutas y handlers de la API de autores. Contiene los endpoints y la inyección de dependencias.
from fastapi import APIRouter, status

from bookstore.authors.dependencies import AuthorServiceDep
from bookstore.authors.schemas import Author, AuthorIn

# Prefijo de la ruta y etiqueta para la documentación de Swagger
router = APIRouter(prefix="/authors", tags=["authors"])


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear un autor")
async def create_author(body: AuthorIn, service: AuthorServiceDep) -> Author:
    """Crea un autor y devuelve el resultado con su identificador."""
    return await service.create(body)


@router.get(
    "/{author_id}",
    summary="Obtener un autor",
    responses={404: {"description": "El autor no existe"}},
)
async def get_author(author_id: int, service: AuthorServiceDep) -> Author:
    """Devuelve un autor por su identificador. Si no existe, un error traducido a 404."""
    return await service.get(author_id)
