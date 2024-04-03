"""empty message

Revision ID: fc483b53e17e
Revises: 
Create Date: 2024-04-02 22:23:47.033462

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fc483b53e17e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Institution', 'city',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('Institution', 'latitude',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('Institution', 'longitude',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('Institution', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('Institution', 'state',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('Institution', 'street',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('Specimen', 'sightingdate',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Specimen', 'sightingdate',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('Institution', 'street',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('Institution', 'state',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('Institution', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('Institution', 'longitude',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.alter_column('Institution', 'latitude',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    op.alter_column('Institution', 'city',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    # ### end Alembic commands ###