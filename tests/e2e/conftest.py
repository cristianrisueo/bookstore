# Fixtures de E2E y smoke: peticiones HTTP reales contra un sistema ya desplegado.
# No levantan nada: `make e2e` despliega la API en contenedores y `make smoke` apunta a donde le digas.
import os
from collections.abc import Iterator

import httpx
import pytest


@pytest.fixture(scope="session")
def base_url() -> str:
    """URL del sistema desplegado. Sin ella se aborta: un E2E que se omite en silencio no prueba nada."""
    url = os.environ.get("BASE_URL")
    if not url:
        raise pytest.UsageError("Falta BASE_URL. Usa `make e2e` o `make smoke BASE_URL=http://...`")
    return url


@pytest.fixture(scope="session")
def client(base_url: str) -> Iterator[httpx.Client]:
    """Cliente HTTP síncrono: contra un sistema remoto no se gana nada con async."""
    with httpx.Client(base_url=base_url, timeout=5) as c:
        yield c
