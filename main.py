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
from app.services.Presentation.power_words.power_words_route import router as power_words_router
from app.services.Presentation.flow_chain.flow_chain_route import router as flow_chain_router
from app.services.Presentation.context_spin.context_spin_route import router as context_spin_router
from app.services.Presentation.precision_drill.precision_drill_route import router as precision_drill_router
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

app.include_router(sight_word_router, prefix="/sight_word_practice", tags=["reading"])
app.include_router(reading_comprehension_router, prefix="/reading_comprehension", tags=["reading"])
app.include_router(phoneme_flashcards_router, prefix="/phoneme_flashcards", tags=["reading"])

app.include_router(power_words_router, prefix="/power_words", tags=["presentation"])
app.include_router(flow_chain_router, prefix="/flow_chain", tags=["presentation"])
app.include_router(context_spin_router, prefix="/context_spin", tags=["presentation"])
app.include_router(precision_drill_router, prefix="/precision_drill", tags=["presentation"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8061)


