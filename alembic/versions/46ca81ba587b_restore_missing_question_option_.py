"""restore missing question option translations

Revision ID: 46ca81ba587b
Revises: ae0be18df63b
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "46ca81ba587b"
down_revision: Union[str, Sequence[str], None] = "ae0be18df63b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "question_option_translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "question_option_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "language",
            sa.String(length=5),
            nullable=False,
        ),
        sa.Column(
            "text",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "review_status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["question_option_id"],
            ["question_options.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "question_option_id",
            "language",
            name="uq_question_option_translation_language",
        ),
    )


def downgrade() -> None:
    op.drop_table("question_option_translations")