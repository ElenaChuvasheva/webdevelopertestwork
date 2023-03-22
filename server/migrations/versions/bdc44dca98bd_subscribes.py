"""subscribes

Revision ID: bdc44dca98bd
Revises: 
Create Date: 2023-03-22 00:35:09.852862

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bdc44dca98bd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instruments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('quotes',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('instrument', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('bid', sa.DECIMAL(), nullable=False),
    sa.Column('offer', sa.DECIMAL(), nullable=False),
    sa.Column('min_amount', sa.DECIMAL(), nullable=False),
    sa.Column('max_amount', sa.DECIMAL(), nullable=False),
    sa.ForeignKeyConstraint(['instrument'], ['instruments.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('subscribes',
    sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('instrument', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['instrument'], ['instruments.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('instrument', 'address', name='instrument_address_constraint')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscribes')
    op.drop_table('quotes')
    op.drop_table('instruments')
    # ### end Alembic commands ###
