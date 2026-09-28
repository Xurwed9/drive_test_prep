from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.state import State
from app.schemas.catalog import StateCatalogItem

router = APIRouter()

@router.get("/states/{state_code}", response_model=StateCatalogItem)
async def get_state(state_code: str, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(State).where(State.code == state_code))
    state = result.scalar_one_or_none()
    if state is None:
        raise HTTPException(status_code=404, detail="State not found",)
    return {
        "code": state.code,
        "name": state.name,
        "status": state.status,
    }