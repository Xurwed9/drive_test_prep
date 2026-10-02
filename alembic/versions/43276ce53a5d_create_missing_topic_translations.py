"""create missing topic translations

Revision ID: 43276ce53a5d
Revises: b15b8510851a
Create Date: 2026-10-02 19:24:58.657557

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "43276ce53a5d"
down_revision: Union[str, Sequence[str], None] = "b15b8510851a"
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