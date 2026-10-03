# Configuración de la aplicación.
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Valores de configuración, validados por Pydantic al arrancar."""

    # Lee automáticamente las variables de entorno desde un archivo .env en la raíz del proyecto.
    # busca el nombre de la variable en mayúsculas y con guiones bajos, por ejemplo: DATABASE_URL
    # Si no existe la variable ni tiene valor por defecto , Pydantic lanzará un error al arrancar.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # DSN y mostrar consultas SQL en la consola (para depuración)
    database_url: str
    sql_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    """
    Devuelve la configuración.  lru_cache guarda el resultado de la primera llamada
    y lo devuelve en las siguientes, evitando leer el archivo .env varias veces.
    """
    return Settings()
