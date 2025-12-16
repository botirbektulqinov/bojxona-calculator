"""add_new_tables

Revision ID: 0002_new_tables
Revises: 0001_initial
Create Date: 2024-12-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_new_tables'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Countries table
    op.create_table('countries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('name_uz', sa.String(length=255), nullable=False),
        sa.Column('name_ru', sa.String(length=255), nullable=True),
        sa.Column('name_en', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_countries_id'), 'countries', ['id'], unique=False)
    op.create_index(op.f('ix_countries_code'), 'countries', ['code'], unique=True)

    # Free Trade Countries table
    op.create_table('free_trade_countries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country_code', sa.String(length=3), nullable=False),
        sa.Column('country_name', sa.String(length=255), nullable=False),
        sa.Column('agreement_name', sa.Text(), nullable=True),
        sa.Column('requires_certificate', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_free_trade_countries_id'), 'free_trade_countries', ['id'], unique=False)
    op.create_index(op.f('ix_free_trade_countries_country_code'), 'free_trade_countries', ['country_code'], unique=True)

    # Utilization Fees table
    op.create_table('utilization_fees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tnved_code_start', sa.String(length=10), nullable=False),
        sa.Column('tnved_code_end', sa.String(length=10), nullable=True),
        sa.Column('fee_type', sa.String(length=20), nullable=False),
        sa.Column('fee_amount', sa.Float(), nullable=True),
        sa.Column('fee_percent', sa.Float(), nullable=True),
        sa.Column('brv_multiplier', sa.Float(), nullable=True),
        sa.Column('engine_volume_min', sa.Integer(), nullable=True),
        sa.Column('engine_volume_max', sa.Integer(), nullable=True),
        sa.Column('vehicle_age_min', sa.Integer(), nullable=True),
        sa.Column('vehicle_age_max', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_url', sa.String(length=512), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_utilization_fees_id'), 'utilization_fees', ['id'], unique=False)
    op.create_index(op.f('ix_utilization_fees_tnved_code_start'), 'utilization_fees', ['tnved_code_start'], unique=False)

    # Tariff Benefits table
    op.create_table('tariff_benefits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tnved_code', sa.String(length=10), nullable=True),
        sa.Column('tnved_code_start', sa.String(length=10), nullable=True),
        sa.Column('tnved_code_end', sa.String(length=10), nullable=True),
        sa.Column('benefit_type', sa.String(length=50), nullable=False),
        sa.Column('reduction_percent', sa.Float(), nullable=True),
        sa.Column('condition_description', sa.Text(), nullable=True),
        sa.Column('requires_certificate', sa.Boolean(), nullable=False, default=False),
        sa.Column('certificate_type', sa.String(length=100), nullable=True),
        sa.Column('valid_from', sa.Date(), nullable=True),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('legal_basis', sa.Text(), nullable=True),
        sa.Column('source_url', sa.String(length=512), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tariff_benefits_id'), 'tariff_benefits', ['id'], unique=False)
    op.create_index(op.f('ix_tariff_benefits_tnved_code'), 'tariff_benefits', ['tnved_code'], unique=False)

    # Customs Fee Rates table
    op.create_table('customs_fee_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('min_customs_value', sa.Float(), nullable=True),
        sa.Column('max_customs_value', sa.Float(), nullable=True),
        sa.Column('fee_type', sa.String(length=20), nullable=False),
        sa.Column('fee_value', sa.Float(), nullable=False),
        sa.Column('min_fee', sa.Float(), nullable=True),
        sa.Column('max_fee', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customs_fee_rates_id'), 'customs_fee_rates', ['id'], unique=False)

    # BRV Rates table
    op.create_table('brv_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('valid_from', sa.Date(), nullable=False),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_brv_rates_id'), 'brv_rates', ['id'], unique=False)
    op.create_index(op.f('ix_brv_rates_year'), 'brv_rates', ['year'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_brv_rates_year'), table_name='brv_rates')
    op.drop_index(op.f('ix_brv_rates_id'), table_name='brv_rates')
    op.drop_table('brv_rates')
    
    op.drop_index(op.f('ix_customs_fee_rates_id'), table_name='customs_fee_rates')
    op.drop_table('customs_fee_rates')
    
    op.drop_index(op.f('ix_tariff_benefits_tnved_code'), table_name='tariff_benefits')
    op.drop_index(op.f('ix_tariff_benefits_id'), table_name='tariff_benefits')
    op.drop_table('tariff_benefits')
    
    op.drop_index(op.f('ix_utilization_fees_tnved_code_start'), table_name='utilization_fees')
    op.drop_index(op.f('ix_utilization_fees_id'), table_name='utilization_fees')
    op.drop_table('utilization_fees')
    
    op.drop_index(op.f('ix_free_trade_countries_country_code'), table_name='free_trade_countries')
    op.drop_index(op.f('ix_free_trade_countries_id'), table_name='free_trade_countries')
    op.drop_table('free_trade_countries')
    
    op.drop_index(op.f('ix_countries_code'), table_name='countries')
    op.drop_index(op.f('ix_countries_id'), table_name='countries')
    op.drop_table('countries')
