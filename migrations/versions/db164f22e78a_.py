"""empty message

Revision ID: db164f22e78a
Revises: c911a1dc8943
Create Date: 2018-04-17 18:54:36.168573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db164f22e78a'
down_revision = 'c911a1dc8943'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('name', sa.String(length=140), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('group_members',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('shares_personal_card', sa.Boolean(), nullable=True),
    sa.Column('shares_work_card', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('addresses', 'card_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('cards', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('cards', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('addresses', 'card_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_table('group_members')
    op.drop_table('groups')
    # ### end Alembic commands ###