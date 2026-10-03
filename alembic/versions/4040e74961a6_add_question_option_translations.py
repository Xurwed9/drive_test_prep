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
    pass


def downgrade() -> None:
    pass