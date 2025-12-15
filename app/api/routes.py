"""API Routes"""
from fastapi import APIRouter
from app.models.schemas import Item, ItemResponse

router = APIRouter(prefix="/api", tags=["items"])


@router.get("/items", response_model=list[ItemResponse])
async def list_items():
    """Get list of items"""
    return []


@router.post("/items", response_model=ItemResponse)
async def create_item(item: Item):
    """Create a new item"""
    return ItemResponse(id=1, **item.model_dump())


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get item by ID"""
    return ItemResponse(id=item_id, name="Sample Item", price=9.99)
