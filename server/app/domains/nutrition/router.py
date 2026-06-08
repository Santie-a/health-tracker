"""Thin HTTP layer for nutrition. Manual + photo meal creation and the day view."""

from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from nutrition_core import MacroTable
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_token
from app.core.config import Settings, get_settings
from app.core.db import get_session

from . import service
from .schemas import DayNutrition, MealCreateResponse, MealIn, MealOut

router = APIRouter(prefix="/meals", tags=["nutrition"], dependencies=[Depends(require_token)])


def get_macro_table(request: Request) -> MacroTable:
    """Shared macro table, loaded once at startup (see app lifespan)."""
    return request.app.state.macro_table


@router.post("", response_model=MealOut, status_code=status.HTTP_201_CREATED)
async def create_meal(
    payload: MealIn,
    session: AsyncSession = Depends(get_session),
    table: MacroTable = Depends(get_macro_table),
) -> MealOut:
    """Manual meal entry. Items with grams but no macros are resolved via nutrition_core."""
    return await service.create_manual_meal(session, payload, table)


@router.post("/photo", response_model=MealCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_from_photo(
    image: UploadFile = File(..., description="Meal photo."),
    name: str | None = Form(None),
    ts: datetime | None = Form(None),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> MealCreateResponse:
    """Photo meal entry: proxied to image-svc. If the GPU box is unreachable the
    response is a degraded empty manual meal (never a 5xx)."""
    raw = await image.read()
    return await service.create_photo_meal(
        session,
        settings,
        raw,
        image.filename or "meal.jpg",
        image.content_type,
        name,
        ts or datetime.now(timezone.utc),
    )


@router.get("", response_model=DayNutrition)
async def meals_for_day(
    date: date = Query(..., description="Day to summarize (YYYY-MM-DD, UTC)."),
    session: AsyncSession = Depends(get_session),
) -> DayNutrition:
    return await service.get_day(session, date)


@router.get("/{meal_id}", response_model=MealOut)
async def get_meal(
    meal_id: int,
    session: AsyncSession = Depends(get_session),
) -> MealOut:
    meal = await service.repository.get(session, meal_id)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found.")
    return MealOut.model_validate(meal)