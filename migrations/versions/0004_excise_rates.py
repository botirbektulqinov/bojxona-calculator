"""add excise_rates table

Revision ID: 0004_excise_rates
Revises: 0003_benefits
Create Date: 2025-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004_excise_rates'
down_revision: Union[str, None] = '0002_new_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'excise_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(100), nullable=False, index=True),
        sa.Column('product_name', sa.String(500), nullable=False),
        sa.Column('product_name_uz', sa.String(500), nullable=True),
        sa.Column('tnved_code_start', sa.String(15), nullable=True, index=True),
        sa.Column('tnved_code_end', sa.String(15), nullable=True),
        sa.Column('import_rate', sa.Float(), nullable=True),
        sa.Column('domestic_rate', sa.Float(), nullable=True),
        sa.Column('rate_unit', sa.String(50), nullable=False),
        sa.Column('is_percentage', sa.Boolean(), default=False),
        sa.Column('article_number', sa.String(20), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_excise_rates_id', 'excise_rates', ['id'])


def downgrade() -> None:
    op.drop_index('ix_excise_rates_id', table_name='excise_rates')
    op.drop_table('excise_rates')
