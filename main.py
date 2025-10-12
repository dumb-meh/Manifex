import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
from app.services.sight_word_practise.sight_word_practise_route import router as sight_word_router

app = FastAPI(
    title="World checker",
    description="An API to check if a word exists in the English dictionary.",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(sight_word_router, tags=["sight-word-practise"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


