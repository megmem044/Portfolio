from fastapi import APIRouter

# Router object is created for health-related endpoints
router = APIRouter()

# Health check endpoint is defined
@router.get("/health")
def health_check():
    # A simple status response is returned
    return {"status": "healthy"}
