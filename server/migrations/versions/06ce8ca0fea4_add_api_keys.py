"""Add API keys

Revision ID: 06ce8ca0fea4
Revises: f63e4dc55168
Create Date: 2022-12-26 17:56:00.070528

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "06ce8ca0fea4"
down_revision = "f63e4dc55168"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "api_key",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("api_key")
    # ### end Alembic commands ###
