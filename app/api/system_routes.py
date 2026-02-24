from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
def health():
    return {"ok": True}
