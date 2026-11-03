from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/tenants", tags=["tenants"])

TENANTS = {
    "infinity": {
        "id": "tenant_infinity",
        "slug": "infinity",
        "name": "Infinity Laghubitta Bittiya Sanstha Ltd.",
        "organization_code": "ILBSL",
        "plan": "enterprise",
        "status": "active",
        "regulatory_class": "D",
        "framework": "NFRS9_NRB",
    }
}


@router.get("")
def list_tenants() -> dict:
    return {"ok": True, "tenants": list(TENANTS.values())}


@router.get("/{slug}")
def get_tenant(slug: str) -> dict:
    tenant = TENANTS.get(slug)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"ok": True, "tenant": tenant}
