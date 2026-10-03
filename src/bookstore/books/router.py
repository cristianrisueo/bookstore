# Rutas y handlers de la API de libros. Contiene los endpoints y la inyección de dependencias.
from fastapi import APIRouter, status

from bookstore.books.dependencies import BookServiceDep
from bookstore.books.schemas import Book, BookIn

# Prefijo de la ruta y etiqueta para la documentación de Swagger
router = APIRouter(prefix="/books", tags=["books"])


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear un libro")
async def create_book(body: BookIn, service: BookServiceDep) -> Book:
    """Crea un libro y devuelve el resultado con su identificador."""
    return await service.create(body)


@router.get(
    "/{book_id}",
    summary="Obtener un libro",
    responses={404: {"description": "El libro no existe"}},
)
async def get_book(book_id: int, service: BookServiceDep) -> Book:
    """Devuelve un libro por su identificador. Si no existe, un error traducido a 404."""
    return await service.get(book_id)
