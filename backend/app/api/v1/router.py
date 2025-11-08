from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, admin, documents, apa, export, stats

api_router = APIRouter()

# Include endpoint routers here
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(apa.router, prefix="/documents", tags=["apa"])
api_router.include_router(export.router, tags=["export"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])

