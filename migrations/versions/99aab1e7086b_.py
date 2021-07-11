"""empty message

Revision ID: 99aab1e7086b
Revises: 
Create Date: 2021-07-10 15:25:30.911710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99aab1e7086b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###
