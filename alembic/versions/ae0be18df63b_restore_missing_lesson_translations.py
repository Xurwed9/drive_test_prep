"""restore missing lesson translations

Revision ID: ae0be18df63b
Revises: 43276ce53a5d
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ae0be18df63b"
down_revision: Union[str, Sequence[str], None] = "43276ce53a5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lesson_translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=5), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "lesson_id",
            "language",
            name="uq_lesson_translation_language",
        ),
    )


def downgrade() -> None:
    op.drop_table("lesson_translations")