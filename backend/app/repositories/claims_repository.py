import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ClaimEvent, IndianHealthClaim


class ClaimsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_claim(self, session_id: str) -> IndianHealthClaim:
        claim = IndianHealthClaim(session_id=session_id, status="DRAFT")
        self.db.add(claim)
        await self.db.flush()  # assigns claim.id without committing yet
        self._log_event(claim.id, "CREATED")
        await self.db.commit()
        await self.db.refresh(claim)
        return claim

    async def update_extracted_data(
        self, claim: IndianHealthClaim, extracted_data: dict, status: str
    ) -> IndianHealthClaim:
        claim.extracted_data = extracted_data
        claim.status = status
        self._log_event(claim.id, "EXTRACTED" if status == "EXTRACTED" else status)
        await self.db.commit()
        await self.db.refresh(claim)
        return claim

    async def get_by_session_id(self, session_id: str) -> IndianHealthClaim | None:
        result = await self.db.execute(
            select(IndianHealthClaim).where(IndianHealthClaim.session_id == session_id)
        )
        return result.scalar_one_or_none()

    def _log_event(self, claim_id: uuid.UUID, event_type: str) -> None:
        self.db.add(ClaimEvent(claim_id=claim_id, event_type=event_type))