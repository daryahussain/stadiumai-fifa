from fastapi import APIRouter, Header
from fastapi.exceptions import HTTPException

from app.core.config import settings

router = APIRouter()


@router.post("/")
async def run_seed(x_admin_key: str = Header(...)):
    if x_admin_key != settings.SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")

    from seed import seed
    result = seed()
    return result
