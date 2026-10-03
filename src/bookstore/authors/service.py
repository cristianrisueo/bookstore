# Capa de servicio de autores. Contiene la lógica de negocio del servicio.
from bookstore.authors.exceptions import AuthorNotFoundError
from bookstore.authors.repository import AuthorRepository
from bookstore.authors.schemas import Author, AuthorIn


class AuthorService:
    def __init__(self, repository: AuthorRepository) -> None:
        """Inicializa el servicio con un repositorio de autores."""
        self._repository = repository

    async def create(self, data: AuthorIn) -> Author:
        """Crea un autor a partir de los datos dados y lo devuelve con su id asignado."""
        return await self._repository.add(data)

    async def get(self, author_id: int) -> Author:
        """Devuelve el autor con el id dado, o lanza AuthorNotFoundError si no existe."""
        author = await self._repository.get(author_id)

        if author is None:
            raise AuthorNotFoundError(author_id)

        return author
