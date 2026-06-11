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
from .schemas import (
    AddItemsIn,
    DayNutrition,
    FoodOut,
    FoodResolveOut,
    MealCreateResponse,
    MealIn,
    MealItemUpdate,
    MealOut,
    MealUpdate,
)

router = APIRouter(prefix="/meals", tags=["nutrition"], dependencies=[Depends(require_token)])
foods_router = APIRouter(prefix="/foods", tags=["nutrition"], dependencies=[Depends(require_token)])


def get_macro_table(request: Request) -> MacroTable:
    """Shared macro table, loaded once at startup (see app lifespan)."""
    return request.app.state.macro_table


# --- foods catalog -----------------------------------------------------------

@foods_router.get("", response_model=list[FoodOut])
async def search_foods(
    q: str | None = Query(None, description="Name/alias substring for autocomplete."),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> list[FoodOut]:
    return await service.search_foods(session, q, limit)


@foods_router.get("/recent", response_model=list[FoodOut])
async def recent_foods(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
) -> list[FoodOut]:
    return await service.recent_foods(session, limit)


@foods_router.get("/resolve", response_model=FoodResolveOut)
async def resolve_food(
    name: str = Query(..., description="Typed food name to resolve via the matcher."),
    session: AsyncSession = Depends(get_session),
    table: MacroTable = Depends(get_macro_table),
) -> FoodResolveOut:
    return await service.resolve_food(session, name, table)


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


@router.patch("/{meal_id}", response_model=MealOut)
async def update_meal(
    meal_id: int,
    payload: MealUpdate,
    session: AsyncSession = Depends(get_session),
) -> MealOut:
    """Edit a meal's name and/or timestamp (fix a wrong entry)."""
    meal = await service.update_meal(session, meal_id, payload)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found.")
    return meal


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal(
    meal_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    if not await service.delete_meal(session, meal_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found.")


@router.post("/{meal_id}/items", response_model=MealOut, status_code=status.HTTP_201_CREATED)
async def add_meal_items(
    meal_id: int,
    payload: AddItemsIn,
    session: AsyncSession = Depends(get_session),
    table: MacroTable = Depends(get_macro_table),
) -> MealOut:
    """Add items to a meal by catalog food (portion×qty or grams), free-text food +
    grams, or a raw kcal-only quick entry."""
    try:
        meal = await service.add_items(session, meal_id, payload, table)
    except service.BadItem as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found.")
    return meal


@router.patch("/{meal_id}/items/{item_id}", response_model=MealOut)
async def update_meal_item(
    meal_id: int,
    item_id: int,
    payload: MealItemUpdate,
    session: AsyncSession = Depends(get_session),
    table: MacroTable = Depends(get_macro_table),
) -> MealOut:
    """Edit a single item; returns the updated meal. Macros re-estimate when grams
    change and aren't pinned explicitly."""
    meal = await service.update_item(session, meal_id, item_id, payload, table)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal item not found.")
    return meal


@router.delete("/{meal_id}/items/{item_id}", response_model=MealOut)
async def delete_meal_item(
    meal_id: int,
    item_id: int,
    session: AsyncSession = Depends(get_session),
) -> MealOut:
    """Remove one item; returns the updated meal."""
    meal = await service.delete_item(session, meal_id, item_id)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal item not found.")
    return meal