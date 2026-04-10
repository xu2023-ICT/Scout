from fastapi import APIRouter

from app.routers.upload import router as upload_router

router = APIRouter()
router.include_router(upload_router)


@router.get("/health")
async def health():
    return {"status": "ok"}
