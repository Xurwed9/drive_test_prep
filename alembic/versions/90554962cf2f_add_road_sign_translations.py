"""add road sign translations

Revision ID: 90554962cf2f
Revises: 34658a75f745
Create Date: 2026-10-02 18:35:46.096116

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "90554962cf2f"
down_revision: Union[str, Sequence[str], None] = "34658a75f745"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "road_sign_translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("road_sign_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=5), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(
            ["road_sign_id"],
            ["road_signs.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "road_sign_id",
            "language",
            name="uq_road_sign_translation_language",
        ),
    )


def downgrade() -> None:
    op.drop_table("road_sign_translations")