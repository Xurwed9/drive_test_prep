"""add lesson translations

Revision ID: 34658a75f745
Revises: cc9669b7ae6d
Create Date: 2026-10-02 17:19:00.569524

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "34658a75f745"
down_revision: Union[str, Sequence[str], None] = "cc9669b7ae6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lesson_translations",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "lesson_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "language",
            sa.String(length=5),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "review_status",
            sa.String(length=30),
            nullable=False,
        ),
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