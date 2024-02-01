"""Added MonitoredAd model

Revision ID: e15fdc073ddb
Revises: 
Create Date: 2024-02-01 12:14:08.620771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e15fdc073ddb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('monitored_ad',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('advertisement_number', sa.String(length=100), nullable=False),
    sa.Column('website_url', sa.String(length=255), nullable=False),
    sa.Column('occurrence_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('monitored_ad')
    # ### end Alembic commands ###
