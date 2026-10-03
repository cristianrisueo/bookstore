# Errores de dominio de libros. Solo heredan de la familia que les corresponde.
from bookstore.core.exceptions import NotFoundError


class BookNotFoundError(NotFoundError):
    """El libro pedido no existe."""

    def __init__(self, book_id: int) -> None:
        super().__init__(f"Book {book_id} not found")
        self.book_id = book_id
