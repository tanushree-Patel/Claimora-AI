import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class IndianMedicalCode(Base):
    __tablename__ = "indian_medical_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code_system: Mapped[str] = mapped_column(String(20), nullable=False)  # "ICD-10" or "SNOMED-CT"
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)

    __table_args__ = (
        Index(
            "ix_indian_medical_codes_display_name_trgm",
            "display_name",
            postgresql_using="gin",
            postgresql_ops={"display_name": "gin_trgm_ops"},
        ),
    )


class IndianHealthClaim(Base):
    __tablename__ = "indian_health_claims"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    abha_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    extracted_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    verified_codes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    irdai_pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ClaimEvent(Base):
    __tablename__ = "claim_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indian_health_claims.id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)  # CREATED, EXTRACTED, etc.
    detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
