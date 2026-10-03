# Smoke: comprobación mínima tras desplegar. No escribe nada, así que es seguro contra cualquier entorno.
import httpx


def test_sistema_vivo_y_conectado(client: httpx.Client) -> None:
    """La API responde y llega a la base de datos."""
    respuesta = client.get("/health/ready")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}
