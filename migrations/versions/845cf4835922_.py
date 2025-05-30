"""empty message

Revision ID: 845cf4835922
Revises: a5cffa318ac2
Create Date: 2025-05-22 07:50:21.381930

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '845cf4835922'
down_revision = 'a5cffa318ac2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('last_name', sa.String(length=150), nullable=False))
        batch_op.add_column(sa.Column('suscription_date', sa.Date(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('suscription_date')
        batch_op.drop_column('last_name')
        batch_op.drop_column('name')

    # ### end Alembic commands ###
