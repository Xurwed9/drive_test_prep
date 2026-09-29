from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b3c3bd891e3"
down_revision: Union[str, Sequence[str], None] = "e40a2d48ba3e"
branch_labels = None
depends_on = None


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