import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
from app.services.Writing.writing_route import router as writing_router
from app.services.Reading.sight_word_practise.sight_word_practice_route import router as sight_word_router
from app.services.Reading.reading_comprehension.reading_comprehension_route import router as reading_comprehension_router
from app.services.Reading.phoneme_flashcards.phoneme_flashcards_route import router as phoneme_flashcards_router
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



app.include_router(writing_router, prefix="/writing", tags=["writing"])
app.include_router(sight_word_router, prefix="/sight_word_practice", tags=["sight_word_practice"])
app.include_router(reading_comprehension_router, prefix="/reading_comprehension", tags=["reading_comprehension"])
app.include_router(phoneme_flashcards_router, prefix="/phoneme_flashcards", tags=["phoneme_flashcards"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8061)


