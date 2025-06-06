"""adds voting table with relationships

Revision ID: 4f5c4d139182
Revises: 4b8725dcb298
Create Date: 2025-04-24 11:03:15.533267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f5c4d139182'
down_revision = '4b8725dcb298'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('votes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('votable_type', sa.String(), nullable=False),
    sa.Column('votable_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_votes_user_id_user')),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'votable_type', 'votable_id', name='unique_vote_constraint')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('votes')
    # ### end Alembic commands ###
