"""add Day table, last_updated to Panel and days to Panel

Revision ID: d39fb58384eb
Revises: 2ab9167a4927
Create Date: 2024-02-23 10:56:27.093923

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd39fb58384eb'
down_revision = '2ab9167a4927'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('days',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('panel_date', sa.DateTime(), nullable=True),
    sa.Column('day_of_week', sa.Integer(), nullable=True),
    sa.Column('day_date_num', sa.Integer(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('is_complete', sa.Boolean(), nullable=True),
    sa.Column('is_pad', sa.Boolean(), nullable=True),
    sa.Column('panel_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['panel_id'], ['panels.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('panels', sa.Column('last_updated', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('panels', 'last_updated')
    op.drop_table('days')
    # ### end Alembic commands ###
