"""add question option translations

Revision ID: 4040e74961a6
Revises: 284be5f87303
Create Date: 2026-10-02 15:05:11.184695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4040e74961a6'
down_revision: Union[str, Sequence[str], None] = '284be5f87303'
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
