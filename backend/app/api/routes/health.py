from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Lightweight health check")
async def health() -> dict[str, str]:
    return {"status": "ok"}
