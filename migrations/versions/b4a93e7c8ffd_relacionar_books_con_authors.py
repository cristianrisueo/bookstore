"""relacionar books con authors

Revision ID: b4a93e7c8ffd
Revises: da16cffb9d8d
Create Date: 2026-10-03 13:20:45.685718

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b4a93e7c8ffd"
down_revision: str | Sequence[str] | None = "da16cffb9d8d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Sustituye books.author (texto) por author_id (FK a authors) conservando los datos.
    Patrón expand -> backfill -> contract: la columna nace nullable, se rellena y solo después se exige.
    """
    # Expand: columna nueva, todavía admite NULL para no fallar con libros existentes
    op.add_column("books", sa.Column("author_id", sa.Integer(), nullable=True))

    # Backfill: un autor por cada nombre distinto que aún no exista, y cada libro apunta al suyo
    op.execute(
        "INSERT INTO authors (name) SELECT DISTINCT b.author FROM books b "
        "WHERE NOT EXISTS (SELECT 1 FROM authors a WHERE a.name = b.author)"
    )
    op.execute("UPDATE books SET author_id = (SELECT min(a.id) FROM authors a WHERE a.name = books.author)")

    # Contract: ya rellena, se exige, se relaciona y se elimina la columna antigua
    op.alter_column("books", "author_id", nullable=False)
    op.create_index(op.f("ix_books_author_id"), "books", ["author_id"], unique=False)
    op.create_foreign_key(op.f("fk_books_author_id_authors"), "books", "authors", ["author_id"], ["id"])
    op.drop_column("books", "author")


def downgrade() -> None:
    """Vuelve a books.author (texto), copiando en ella el nombre de cada autor. La tabla authors se conserva."""
    op.add_column("books", sa.Column("author", sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.execute("UPDATE books SET author = a.name FROM authors a WHERE a.id = books.author_id")
    op.alter_column("books", "author", nullable=False)

    op.drop_constraint(op.f("fk_books_author_id_authors"), "books", type_="foreignkey")
    op.drop_index(op.f("ix_books_author_id"), table_name="books")
    op.drop_column("books", "author_id")
