"""add panel position column

Revision ID: ec070c72a627
Revises: 176f869e40db
Create Date: 2023-08-24 22:05:40.177204

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec070c72a627'
down_revision = '176f869e40db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('panels', sa.Column('position', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('panels', 'position')
    # ### end Alembic commands ###
