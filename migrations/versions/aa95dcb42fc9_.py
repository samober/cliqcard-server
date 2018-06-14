"""empty message

Revision ID: aa95dcb42fc9
Revises: 2805febc4a10
Create Date: 2018-06-14 14:27:23.990050

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'aa95dcb42fc9'
down_revision = '2805febc4a10'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('phone_tokens', sa.Column('code', sa.String(length=8), nullable=False))
    op.add_column('phone_tokens', sa.Column('expires_in', sa.Integer(), nullable=False))
    op.add_column('phone_tokens', sa.Column('issued_at', sa.Integer(), nullable=False))
    op.drop_column('phone_tokens', 'validation_code')
    op.drop_column('phone_tokens', 'created_at')
    op.drop_column('phone_tokens', 'expiration')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('phone_tokens', sa.Column('expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.add_column('phone_tokens', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.add_column('phone_tokens', sa.Column('validation_code', sa.VARCHAR(length=8), autoincrement=False, nullable=False))
    op.drop_column('phone_tokens', 'issued_at')
    op.drop_column('phone_tokens', 'expires_in')
    op.drop_column('phone_tokens', 'code')
    # ### end Alembic commands ###