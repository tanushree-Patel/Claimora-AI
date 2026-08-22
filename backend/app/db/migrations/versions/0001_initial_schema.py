"""initial schema: extensions, medical codes, claims, claim events"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "indian_medical_codes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code_system", sa.String(20), nullable=False),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("display_name", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("embedding", Vector(768), nullable=True),
    )
    op.execute(
        "CREATE INDEX ix_indian_medical_codes_display_name_trgm "
        "ON indian_medical_codes USING gin (display_name gin_trgm_ops)"
    )

    op.create_table(
        "indian_health_claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", sa.String(64), nullable=False, unique=True),
        sa.Column("abha_id", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="DRAFT"),
        sa.Column("extracted_data", postgresql.JSONB, nullable=True),
        sa.Column("verified_codes", postgresql.JSONB, nullable=True),
        sa.Column("irdai_pdf_url", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "claim_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "claim_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("indian_health_claims.id"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("detail", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("claim_events")
    op.drop_table("indian_health_claims")
    op.execute("DROP INDEX IF EXISTS ix_indian_medical_codes_display_name_trgm")
    op.drop_table("indian_medical_codes")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS vector")
