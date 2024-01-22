"""add last_login to User

Revision ID: 490fd05774cc
Revises: 08ab49254135
Create Date: 2024-01-22 13:47:59.295498

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '490fd05774cc'
down_revision = '08ab49254135'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_login')
    # ### end Alembic commands ###
