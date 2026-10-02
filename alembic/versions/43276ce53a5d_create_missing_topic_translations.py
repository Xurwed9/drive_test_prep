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
    pass


def downgrade() -> None:
    pass