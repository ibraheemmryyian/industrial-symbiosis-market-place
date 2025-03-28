from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1.api import router as api_router

app = FastAPI(
    title="Industrial Symbiosis Marketplace",
    description="AI-powered platform for matching industrial waste producers with potential users",
    version=settings.VERSION
)

# Configure CORS (adjust allowed origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Create database tables if they don't exist
@app.on_event("startup")
async def startup():
    from app.db.base_class import Base
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Industrial Symbiosis Marketplace API",
        "version": settings.VERSION,
        "status": "active"
    }
