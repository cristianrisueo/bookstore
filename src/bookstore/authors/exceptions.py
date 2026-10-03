# Errores de dominio de autores. Solo heredan de la familia que les corresponde.
from bookstore.core.exceptions import NotFoundError


class AuthorNotFoundError(NotFoundError):
    """El autor pedido no existe."""

    def __init__(self, author_id: int) -> None:
        super().__init__(f"Author {author_id} not found")
        self.author_id = author_id
