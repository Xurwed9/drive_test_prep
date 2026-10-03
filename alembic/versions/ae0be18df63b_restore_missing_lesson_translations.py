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
    pass


def downgrade() -> None:
    pass