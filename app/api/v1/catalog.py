from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.models.state import State
from app.db.session import get_db
from app.schemas.catalog import CatalogResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/catalog", response_model=CatalogResponse)
async def get_catalog(
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(State)
    )

    states = result.scalars().all()

    return {
        "states": [
            {
                "code": state.code,
                "name": state.name,
                "status": state.status,
            }
            for state in states
        ]
    }