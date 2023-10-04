"""add event_id to timings table

Revision ID: cbee85208c46
Revises: af513b19333e
Create Date: 2023-10-03 23:24:39.431008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbee85208c46'
down_revision = 'af513b19333e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('timings', sa.Column('event_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('timings', 'event_id')
    # ### end Alembic commands ###