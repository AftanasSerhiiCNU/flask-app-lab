"""Add User Post relationship

Revision ID: ea0181964dbe
Revises: 68ff20a5291a
Create Date: 2026-11-20 21:00:07.874429
"""

from alembic import op
import sqlalchemy as sa

revision = "ea0181964dbe"
down_revision = "68ff20a5291a"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_posts_user_id", "users", ["user_id"], ["id"])
        batch_op.drop_column("author")


def downgrade():
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "author",
                sa.String(length=20),
                server_default="Anonymous",
                nullable=False,
            )
        )
        batch_op.drop_constraint("fk_posts_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")
