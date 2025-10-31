"""Add ai_generations table

Revision ID: add_ai_generations
Revises: add_notes_favorites
Create Date: 2025-10-31 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_ai_generations"
down_revision: Union[str, Sequence[str], None] = "add_notes_favorites"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ai_generations table
    op.create_table(
        "ai_generations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("note_ids", sa.ARRAY(sa.Integer()), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("ai_provider", sa.String(length=50), nullable=False),
        sa.Column("generated_content", sa.Text(), nullable=False),
        sa.Column(
            "created_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ai_generations_id"), "ai_generations", ["id"], unique=False
    )
    op.create_index(
        "idx_user_created",
        "ai_generations",
        ["user_id", "created_date"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_user_created", table_name="ai_generations", if_exists=True)
    op.drop_index(op.f("ix_ai_generations_id"), table_name="ai_generations")
    op.drop_table("ai_generations")
