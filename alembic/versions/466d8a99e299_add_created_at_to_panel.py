"""add created_at to panel

Revision ID: 466d8a99e299
Revises: ec070c72a627
Create Date: 2023-08-29 10:31:58.663806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '466d8a99e299'
down_revision = 'ec070c72a627'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('panels', sa.Column('created_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('panels', 'created_at')
    # ### end Alembic commands ###
