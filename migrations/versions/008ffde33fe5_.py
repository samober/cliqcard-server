"""empty message

Revision ID: 008ffde33fe5
Revises: 3a8d7fe5c15d
Create Date: 2018-04-17 14:15:42.748474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008ffde33fe5'
down_revision = '3a8d7fe5c15d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('phone_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=False),
    sa.Column('validation_code', sa.String(length=8), nullable=False),
    sa.Column('new_phone_number', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('phone_tokens')
    # ### end Alembic commands ###