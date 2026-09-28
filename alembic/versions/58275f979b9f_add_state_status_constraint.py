"""add state status constraint

Revision ID: 58275f979b9f
Revises: 48b43ef27a69
Create Date: 2026-09-24 16:14:32.830730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58275f979b9f'
down_revision: Union[str, Sequence[str], None] = '48b43ef27a69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        'uq_content_versions_scope_version',
        'content_versions',
        ['state_id', 'vehicle_id', 'module_id', 'version'],
    )

    op.create_unique_constraint(
        'uq_lessons_topic_order',
        'lessons',
        ['topic_id', 'order'],
    )

    op.create_unique_constraint(
        'uq_translations_question_language',
        'translations',
        ['question_id', 'language'],
    )

    op.create_check_constraint(
        'ck_states_status',
        'states',
        "status IN ('available', 'coming_soon')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'ck_states_status',
        'states',
        type_='check',
    )

    op.drop_constraint(
        'uq_translations_question_language',
        'translations',
        type_='unique',
    )

    op.drop_constraint(
        'uq_lessons_topic_order',
        'lessons',
        type_='unique',
    )

    op.drop_constraint(
        'uq_content_versions_scope_version',
        'content_versions',
        type_='unique',
    )
