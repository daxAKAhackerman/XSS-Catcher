"""Remove default values

Revision ID: f63e4dc55168
Revises: a994d989e1d7
Create Date: 2022-12-26 18:28:01.958620

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f63e4dc55168"
down_revision = "a994d989e1d7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("settings", schema=None) as batch_op:
        batch_op.alter_column("webhook_type", server_default=None)
        batch_op.alter_column("starttls", server_default=None)
        batch_op.alter_column("ssl_tls", server_default=None)

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column("first_login", server_default=None)
        batch_op.alter_column("is_admin", server_default=None)

    with op.batch_alter_table("xss", schema=None) as batch_op:
        batch_op.alter_column("tags", server_default=None)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("settings", schema=None) as batch_op:
        batch_op.alter_column("webhook_type", server_default="0")
        batch_op.alter_column("starttls", server_default=sa.text("0"))
        batch_op.alter_column("ssl_tls", server_default=sa.text("0"))

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column("first_login", server_default=sa.text("1"))
        batch_op.alter_column("is_admin", server_default=sa.text("0"))

    with op.batch_alter_table("xss", schema=None) as batch_op:
        batch_op.alter_column("tags", server_default="[]")

    # ### end Alembic commands ###