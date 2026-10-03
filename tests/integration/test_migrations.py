# Migraciones de Alembic. Cada test trabaja en su propia base de datos vacía (bd_migraciones).
from collections.abc import Callable

# La fixture alembic del conftest: alembic(url, *argumentos)
type AlembicRunner = Callable[..., None]


def test_modelos_y_migraciones_coinciden(bd_migraciones: str, alembic: AlembicRunner) -> None:
    """
    Tras aplicar todas las migraciones, alembic check no detecta diferencias con los modelos.
    Caza una migración olvidada después de tocar un modelo. Ojo: no compara los CHECK.
    """
    alembic(bd_migraciones, "upgrade", "head")
    alembic(bd_migraciones, "check")


def test_migraciones_bajan_y_suben_en_vacio(bd_migraciones: str, alembic: AlembicRunner) -> None:
    """Todas las migraciones se pueden deshacer y volver a aplicar: caza downgrades rotos."""
    alembic(bd_migraciones, "upgrade", "head")
    alembic(bd_migraciones, "downgrade", "base")
    alembic(bd_migraciones, "upgrade", "head")
