"""init

Revision ID: f5c19cb60c9d
Revises: 
Create Date: 2019-01-07 10:58:11.757695

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5c19cb60c9d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'albums', 'artists', ['artist_id'], ['id'])
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_constraint(None, 'albums', type_='foreignkey')
    # ### end Alembic commands ###
