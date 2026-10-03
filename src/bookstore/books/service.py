# Capa de servicio de libros. Contiene la lógica de negocio del servicio.
from bookstore.authors.service import AuthorService
from bookstore.books.exceptions import BookNotFoundError
from bookstore.books.repository import BookRepository
from bookstore.books.schemas import Book, BookIn


class BookService:
    def __init__(self, repository: BookRepository, author_service: AuthorService) -> None:
        """Inicializa el servicio con su repositorio y el servicio de autores."""
        self._repository = repository
        self._author_service = author_service

    async def create(self, data: BookIn) -> Book:
        """Crea un libro si su autor existe. Si no, lanza AuthorNotFoundError (404)."""
        await self._author_service.get(data.author_id)
        return await self._repository.add(data)

    async def get(self, book_id: int) -> Book:
        """Devuelve el libro con el id dado, o lanza BookNotFoundError si no existe."""
        book = await self._repository.get(book_id)

        if book is None:
            raise BookNotFoundError(book_id)

        return book
