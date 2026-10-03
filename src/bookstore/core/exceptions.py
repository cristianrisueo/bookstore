# Errores de negocio, compartidas por todos los dominios.
# Cada dominio hereda de la que le corresponde; ninguno sabe nada de HTTP.


class DomainError(Exception):
    """Base de todos los errores de negocio de la aplicación."""


class NotFoundError(DomainError):
    """El recurso pedido no existe."""


class ConflictError(DomainError):
    """La operación choca con el estado actual (por ejemplo, un duplicado)."""
