# Bookstore API

API de práctica con FastAPI organizada por dominios: libros y autores sobre PostgreSQL, con SQLAlchemy asíncrono y migraciones con Alembic. Sirve de banco de pruebas para la arquitectura que usará Locker API.

## Stack

| Pieza                          | Para qué se usa                                                         |
| ------------------------------ | ----------------------------------------------------------------------- |
| Python 3.14 y uv               | Lenguaje, entorno virtual y dependencias (`pyproject.toml` + `uv.lock`) |
| FastAPI y Uvicorn              | Framework web (rutas, validación, documentación) y servidor ASGI        |
| Pydantic y pydantic-settings   | Contrato de la API y configuración desde variables de entorno           |
| SQLAlchemy 2 (async) y asyncpg | Acceso a PostgreSQL                                                     |
| Alembic                        | Migraciones del esquema                                                 |
| PostgreSQL en Docker           | Base de datos (`compose.yml`)                                           |
| Ruff y mypy (strict)           | Formateo, linter y comprobación de tipos                                |

## Puesta en marcha

Copia la plantilla de variables de entorno. En local, los valores son los de `compose.yml`, así que no hace falta cambiar nada:

```bash
cp .env.example .env
```

El valor de ejemplo es:

```
DATABASE_URL=postgresql+asyncpg://bookstore:bookstore@localhost:5432/bookstore
```

El `+asyncpg` es obligatorio: sin él, SQLAlchemy usaría un driver síncrono y la API no arrancaría.

Y después:

```bash
uv sync        # instala las dependencias en .venv
make up        # levanta PostgreSQL
make migrate   # aplica las migraciones
make run       # arranca la API en http://127.0.0.1:8000 (documentación en /docs)
```

Escribe `make` para ver todos los comandos disponibles.

| Comando                          | Qué hace                                              |
| -------------------------------- | ----------------------------------------------------- |
| `make up` / `make stop`          | Levanta o apaga el contenedor de PostgreSQL           |
| `make down`                      | Elimina el contenedor (los datos se conservan)        |
| `make destroy`                   | Elimina el contenedor **y los datos**                 |
| `make psql`                      | Abre una consola SQL dentro de la base de datos       |
| `make migration m="mensaje"`     | Genera una migración a partir de los modelos          |
| `make migrate` / `make rollback` | Aplica las migraciones pendientes o deshace la última |
| `make run`                       | Arranca la API con recarga automática                 |
| `make check`                     | Formatea, pasa el linter y comprueba los tipos        |

## Arquitectura

El código está organizado **por dominio**, no por tipo de archivo. Cada dominio es un paquete con todo lo que necesita, y todos los dominios tienen exactamente la misma estructura, de modo que quien entiende uno entiende los demás. Lo que comparten todos vive en `core/`.

```
src/bookstore/
├── main.py                   # crea la aplicación y la ensambla
├── core/                     # lo que comparten todos los dominios
│   ├── config.py
│   ├── database.py
│   ├── exceptions.py
│   └── exception_handlers.py
├── authors/                  # dominio de autores
│   ├── router.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── service.py
│   ├── repository.py
│   ├── models.py
│   └── exceptions.py
└── books/                    # dominio de libros (misma estructura)
migrations/
├── env.py                    # configuración de Alembic
└── versions/                 # una migración por archivo
```

### Qué hace cada archivo de un dominio

| Archivo           | Responsabilidad                                                                                                                                                                       | ¿Conoce HTTP?  | ¿Conoce la base de datos? |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------------------- |
| `router.py`       | Los endpoints. Traduce una petición HTTP en una llamada al servicio y devuelve su resultado. No toma decisiones de negocio.                                                           | Sí             | No                        |
| `schemas.py`      | Modelos de Pydantic: el contrato público de la API, separado en entrada (`BookIn`) y salida (`Book`).                                                                                 | Es su contrato | No                        |
| `dependencies.py` | El cableado con `Depends`: construye el repositorio y el servicio en cada petición.                                                                                                   | Sí             | Solo recibe la sesión     |
| `service.py`      | Las reglas de negocio. Lanza errores de dominio cuando una regla no se cumple.                                                                                                        | No             | No                        |
| `repository.py`   | El acceso a datos: una interfaz (`Protocol`) y su implementación sobre PostgreSQL. Convierte los modelos de SQLAlchemy en schemas de Pydantic, de modo que nada del ORM sale de aquí. | No             | Sí                        |
| `models.py`       | Las tablas, como clases de SQLAlchemy.                                                                                                                                                | No             | Sí                        |
| `exceptions.py`   | Los errores de negocio del dominio, que heredan de las familias de `core`.                                                                                                            | No             | No                        |

### Qué hay en `core/`

| Archivo                 | Responsabilidad                                                                                                                                                                          |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `config.py`             | La configuración global. Se lee de las variables de entorno y, si no están, del `.env`, con validación al arrancar.                                                                      |
| `database.py`           | El motor (pool de conexiones), la fábrica de sesiones, la clase `Base` de todas las tablas con su convención de nombres, y la dependencia `get_session`, que da una sesión por petición. |
| `exceptions.py`         | Las familias de errores de negocio: `DomainError`, `NotFoundError` y `ConflictError`. No saben nada de HTTP.                                                                             |
| `exception_handlers.py` | El único sitio donde un error de dominio se convierte en respuesta HTTP: `NotFoundError` en 404 y `ConflictError` en 409.                                                                |

### El recorrido de una petición

```
HTTP ──► router ──► service ──► repository ──► PostgreSQL
                       ▲
          dependencies construye la cadena en cada petición:
          get_session ─► repositorio ─► servicio

Respuesta: modelo de SQLAlchemy ─► schema de Pydantic ─► JSON

Error:     el servicio lanza un error de dominio (por ejemplo, BookNotFoundError)
           ─► core/exception_handlers lo traduce por herencia ─► 404 o 409
```

### Reglas de dependencia

Dentro de un dominio, las importaciones van en una sola dirección: `router` → `dependencies` → `service` → `repository` → `models`. Los `schemas` los usan el router, el servicio y el repositorio. Ningún archivo importa a uno que esté por encima de él, y así no hay imports circulares.

Entre dominios, `books` depende de `authors` y nunca al revés. El servicio de libros usa el servicio de autores (por `id`), el modelo de libros referencia al de autores para la clave foránea, y la respuesta de un libro anida el schema de autor.

`core` no importa ningún dominio; los dominios sí importan `core`. `main.py` es el único que importa todo, para ensamblar la aplicación.

## Decisiones de diseño

**Schemas y modelos separados.** El contrato de la API y el esquema de la base de datos son contratos distintos: uno es público y el otro interno. Separarlos permite cambiar la base de datos sin romper a los clientes, y ocultar o transformar campos (por ejemplo, la entrada recibe `author_id` y la salida devuelve el autor anidado).

**Errores de dominio sin HTTP.** Los servicios lanzan errores con significado de negocio y no saben qué código HTTP les corresponde. La traducción está centralizada en `core` y funciona por herencia, así que un dominio nuevo no necesita manejadores propios.

**Commit en el repositorio.** Cada escritura confirma su propia transacción. Es suficiente mientras cada operación toque una sola tabla. Cuando una operación escriba en varias tablas, el commit se moverá al servicio para que todo vaya en la misma transacción.

**Relaciones cargadas explícitamente.** Las relaciones se declaran con `lazy="raise"` y se cargan con `selectinload` donde se necesitan. Si se accede a una relación sin cargarla, el error es claro, en lugar del `MissingGreenlet` propio de SQLAlchemy asíncrono.

**Integridad en dos capas.** Un libro necesita un autor existente. El servicio lo comprueba para devolver un 404 claro, y la clave foránea de PostgreSQL lo garantiza siempre, incluso si el autor se borra entre la comprobación y el insert. Ese último caso hoy devuelve un 500 y está pendiente de traducir.

**Convención de nombres.** Índices, restricciones únicas y claves foráneas tienen nombres predecibles (`ix_books_author_id`, `fk_books_author_id_authors`), lo que permite deshacer migraciones y entender los errores de PostgreSQL sin abrir el código.

## Migraciones

Las migraciones no se aplican solas al arrancar. El flujo es: modificar los modelos, generar la migración con `make migration m="..."`, **revisarla siempre** (el autogenerate no lo detecta todo y puede generar migraciones vacías) y aplicarla con `make migrate`. En los despliegues, se aplican como un paso del pipeline, antes de desplegar el código nuevo.

Cada dominio debe importar su `models.py` en `migrations/env.py`. Sin ese import, Alembic no ve sus tablas.

## Añadir un dominio nuevo

| Paso | Qué hacer                                                                                                                                    |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Crear la carpeta del dominio con su `__init__.py` vacío                                                                                      |
| 2    | Escribir `models.py` e importarlo en `migrations/env.py`                                                                                     |
| 3    | Generar la migración, revisarla y aplicarla                                                                                                  |
| 4    | Escribir `schemas.py` y `exceptions.py` (heredando de `core`)                                                                                |
| 5    | Escribir `repository.py`, `service.py` y `dependencies.py`, con el nombre del dominio en las funciones de dependencia (`get_author_service`) |
| 6    | Escribir `router.py` y registrarlo en `main.py` con `include_router`                                                                         |
| 7    | Pasar `make check`                                                                                                                           |

## Tests

Pendientes. Se ejecutarán contra un PostgreSQL real y efímero (testcontainers), no contra repositorios en memoria, para que reflejen el comportamiento real de restricciones, transacciones y concurrencia.
