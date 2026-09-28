"""add active content version constraints

Revision ID: ef27f69af383
Revises: 8b94c5b9ca3a
Create Date: 2026-09-26 16:26:12.669440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef27f69af383'
down_revision: Union[str, Sequence[str], None] = '8b94c5b9ca3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_active_content_version_no_module",
        "content_versions",
        ["state_id", "vehicle_id"],
        unique=True,
        postgresql_where=sa.text(
            "available = true AND module_id IS NULL"
        ),
    )

    op.create_index(
        "uq_active_content_version_with_module",
        "content_versions",
        ["state_id", "vehicle_id", "module_id"],
        unique=True,
        postgresql_where=sa.text(
            "available = true AND module_id IS NOT NULL"
        ),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_active_content_version_with_module",
        table_name="content_versions",
    )

    op.drop_index(
        "uq_active_content_version_no_module",
        table_name="content_versions",
    )
