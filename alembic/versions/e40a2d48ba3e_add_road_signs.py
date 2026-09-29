"""Add road signs

Revision ID: e40a2d48ba3e
Revises: 096b022de674
Create Date: 2026-09-29 13:51:22.253869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e40a2d48ba3e'
down_revision: Union[str, Sequence[str], None] = '096b022de674'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "road_signs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content_version_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["content_version_id"],
            ["content_versions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("road_signs")