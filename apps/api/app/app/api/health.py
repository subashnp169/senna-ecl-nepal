from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "service": "senna-ecl-cloud-api",
        "version": "0.1.0",
        "readiness": "research_and_pilot_scaffold",
    }
