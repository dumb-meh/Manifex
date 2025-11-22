import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.api.v1.routes import api_router
from app.utils.temp_cleanup import start_cleanup_service
app = FastAPI(
    title="Writing AI API",
    description="An API for AI-powered writing assistance with topic generation and scoring.",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Include API v1 routes with versioning
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Start background services when the app starts"""

    temp_dir = Path("temp_audio")
    temp_dir.mkdir(exist_ok=True)
    
    asyncio.create_task(start_cleanup_service())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8061)


