# Configuración de Alembic: cómo se conecta a la base de datos y qué tablas conoce.
# Se ejecuta cada vez que lanza un comando de Alembic (upgrade, revision...).
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Importa los modelos registra sus tablas en Base.metadata. No borrar aunque parezcan sin uso
from bookstore.authors import models as authors_models  # noqa: F401
from bookstore.books import models as books_models  # noqa: F401
from bookstore.core.config import get_settings
from bookstore.core.database import Base

# Configuración leída de alembic.ini
config = context.config

# La URL sale de config.py (del .env o del entorno), no de alembic.ini.
# Así la app y las migraciones usan siempre la misma base de datos
config.set_main_option("sqlalchemy.url", get_settings().database_url)

# Configura los logs de Alembic según alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Las tablas que Alembic compara con la base de datos para generar migraciones.
# Cada dominio nuevo debe importar arriba sus modelos para aparecer aquí
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Modo offline: genera el SQL sin conectarse (alembic upgrade head --sql)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Ejecuta las migraciones sobre una conexión ya abierta."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Modo online: abre una conexión async y ejecuta las migraciones en ella."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # sin pool: es un proceso corto que abre una conexión y termina
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Punto de entrada del modo online."""
    asyncio.run(run_async_migrations())


# Alembic decide el modo según el comando que lances
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
