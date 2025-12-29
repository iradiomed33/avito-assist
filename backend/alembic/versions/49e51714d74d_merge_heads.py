"""merge heads

Revision ID: 49e51714d74d
Revises: 19eaa2c448ef, e59ef775f373
Create Date: 2025-12-29 19:29:50.875105

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "49e51714d74d"
down_revision = ('19eaa2c448ef', 'e59ef775f373')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
