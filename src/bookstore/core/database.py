# Conexión a la base de datos.
# Este archivo prepara tres cosas: el pool de conexiones, las sesiones y la base de las tablas.
from collections.abc import AsyncIterator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from bookstore.core.config import get_settings

# Convención de nombres para índices, restricciones únicas y claves foráneas.
# Así todas tienen un nombre predecible y Alembic puede borrarlas al deshacer una migración
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}


# Lee la configuración (la URL de la base de datos) del .env
settings = get_settings()

# ENGINE: el pool de conexiones a Postgres. Hay uno solo para toda la aplicación.
# Crearlo no conecta todavía: las conexiones se abren cuando hacen falta y se reutilizan.
engine = create_async_engine(settings.database_url, echo=settings.sql_echo)

# FÁBRICA DE SESIONES: crea sesiones ya configuradas, para no repetir la configuración.
# expire_on_commit=False: tras guardar los cambios (commit), los objetos conservan
# sus valores en memoria. Si no, Python intentaría releerlos de la base de datos
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """
    Base es la clase de la que heredan todas las tablas (BookModel, UserModel...).
    Al heredar, cada tabla queda registrada, y así Alembic sabe qué tablas existen.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependencia de FastAPI: una sesión por petición, que se cierra al terminar."""
    async with SessionFactory() as session:
        yield session
