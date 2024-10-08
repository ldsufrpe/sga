"""Adicionar campo is_admin no modelo User

Revision ID: c66005a178a7
Revises: 668e097cf587
Create Date: 2024-09-08 11:06:06.795458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c66005a178a7'
down_revision = '668e097cf587'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=120),
               existing_nullable=False)
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=128),
               existing_nullable=False)
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=150), nullable=False))
        batch_op.alter_column('password',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.String(length=120),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)
        batch_op.drop_column('is_admin')

    # ### end Alembic commands ###
