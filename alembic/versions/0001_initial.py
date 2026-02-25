"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-06 00:00:00.000000

"""

import sqlalchemy as sa  # noqa

from alembic import op  # noqa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This file exists for educational purposes and for CI checks.
    pass


def downgrade() -> None:
    pass
