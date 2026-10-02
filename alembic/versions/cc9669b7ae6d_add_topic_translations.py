"""add topic translations

Revision ID: cc9669b7ae6d
Revises: 4040e74961a6
Create Date: 2026-10-02 17:17:03.121244

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cc9669b7ae6d"
down_revision: Union[str, Sequence[str], None] = "4040e74961a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "topic_translations",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "topic_id",
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
            "review_status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["topics.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "topic_id",
            "language",
            name="uq_topic_translation_language",
        ),
    )


def downgrade() -> None:
    op.drop_table("topic_translations")