"""adds content limits and adds submitted_by_id to article

Revision ID: 0e9b7f200195
Revises: 2b3b68607a30
Create Date: 2025-04-19 17:42:49.599826
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0e9b7f200195'
down_revision = '2b3b68607a30'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(length=150), nullable=False))
        batch_op.add_column(sa.Column('url', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('submitted_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            batch_op.f('fk_article_submitted_by_id_user'),
            'user',
            ['submitted_by_id'],
            ['id'],
            ondelete='CASCADE'
        )
        #batch_op.drop_column('content')
        #batch_op.drop_column('user_id')

    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.alter_column('user_id', existing_type=sa.INTEGER(), nullable=True)  # Keep this as it is
        # Drop the existing foreign key constraints
        batch_op.drop_constraint('fk_comment_article_id_article', type_='foreignkey')
        batch_op.drop_constraint('fk_comment_user_id_user', type_='foreignkey')
        
        # Create a new foreign key with the 'SET NULL' on delete option
        batch_op.create_foreign_key(
            batch_op.f('fk_comment_user_id_user'),
            'user',
            ['user_id'],
            ['id'],
            ondelete='SET NULL'
        )

        batch_op.create_foreign_key(
            batch_op.f('fk_comment_article_id_article'),
            'article',
            ['article_id'],
            ['id'],
            ondelete='CASCADE'
        )

    with op.batch_alter_table('fact_check', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content', sa.String(length=2000), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('updated_at')


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DATETIME(), nullable=True))

    with op.batch_alter_table('fact_check', schema=None) as batch_op:
        batch_op.drop_column('content')

    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_comment_article_id_article'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_comment_user_id_user'), type_='foreignkey')
        batch_op.create_foreign_key('fk_comment_user_id_user', 'user', ['user_id'], ['id'])
        batch_op.create_foreign_key('fk_comment_article_id_article', 'article', ['article_id'], ['id'])
        batch_op.alter_column('user_id', existing_type=sa.INTEGER(), nullable=False)

    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('content', sa.VARCHAR(), nullable=False))
        batch_op.drop_constraint(batch_op.f('fk_article_submitted_by_id_user'), type_='foreignkey')
        batch_op.create_foreign_key('fk_article_user_id_user', 'user', ['user_id'], ['id'])
        batch_op.drop_column('submitted_by_id')
        batch_op.drop_column('url')
        batch_op.drop_column('title')
