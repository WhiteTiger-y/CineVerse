"""Add OTP fields to users and create chat_messages

Revision ID: 20250918_otp_and_chat
Revises: 
Create Date: 2025-09-18
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250918_otp_and_chat'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users table OTP fields
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column('otp_code', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('otp_expires_at', sa.DateTime(), nullable=True))
        # Remove default after set
    op.execute("UPDATE users SET is_verified = false WHERE is_verified IS NULL;")
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('is_verified', server_default=None)

    # chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.String(), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('sender', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('chat_messages')
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('otp_expires_at')
        batch_op.drop_column('otp_code')
        batch_op.drop_column('is_verified')
