"""Add segment column to chunks

Revision ID: 394cf5ba98e1
Revises: f9438b502887
Create Date: 2026-10-27 15:21:48.264780

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "394cf5ba98e1"
down_revision: str | Sequence[str] | None = "f9438b502887"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "chunks",
        sa.Column("segment", sa.String(), nullable=False, server_default="all"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("chunks", "segment")
