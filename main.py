import uvicorn
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
from pathlib import Path
from app.services.Writing.writing_route import router as writing_router
from app.services.Reading.sight_word_practise.sight_word_practice_route import router as sight_word_router
from app.services.Reading.reading_comprehension.reading_comprehension_route import router as reading_comprehension_router
from app.services.Reading.phoneme_flashcards.phoneme_flashcards_route import router as phoneme_flashcards_router
from app.services.Presentation.power_words.power_words_route import router as power_words_router
from app.services.Presentation.flow_chain.flow_chain_route import router as flow_chain_router
from app.services.Presentation.context_spin.context_spin_route import router as context_spin_router
from app.services.Presentation.precision_drill.precision_drill_route import router as precision_drill_router
from app.services.Speaking.listen_speak.listen_speak_route import router as listen_speak_router
from app.services.Speaking.phrase_repeat.phrase_repeat_route import router as phrase_repeat_router
from app.services.Speaking.pronunciation.pronunciation_route import router as pronunciation_router
from app.services.Speaking.vocabulary_challenge.vocabulary_challenge_route import router as vocabulary_challenge_router
from app.services.Adult.word_flash.word_flash_route import router as word_flash_router
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



app.include_router(writing_router, prefix="/writing", tags=["writing"])

app.include_router(sight_word_router, prefix="/sight_word_practice", tags=["reading"])
app.include_router(reading_comprehension_router, prefix="/reading_comprehension", tags=["reading"])
app.include_router(phoneme_flashcards_router, prefix="/phoneme_flashcards", tags=["reading"])

app.include_router(power_words_router, prefix="/power_words", tags=["presentation"])
app.include_router(flow_chain_router, prefix="/flow_chain", tags=["presentation"])
app.include_router(context_spin_router, prefix="/context_spin", tags=["presentation"])
app.include_router(precision_drill_router, prefix="/precision_drill", tags=["presentation"])

app.include_router(listen_speak_router, prefix="/listen_speak", tags=["speaking"])
app.include_router(phrase_repeat_router, prefix="/phrase_repeat", tags=["speaking"])
app.include_router(pronunciation_router, prefix="/pronunciation", tags=["speaking"])
app.include_router(vocabulary_challenge_router, prefix="/vocabulary_challenge", tags=["speaking"])

app.include_router(word_flash_router, prefix="/word_flash", tags=["adult"])

@app.on_event("startup")
async def startup_event():
    """Start background services when the app starts"""

    temp_dir = Path("temp_audio")
    temp_dir.mkdir(exist_ok=True)
    
    asyncio.create_task(start_cleanup_service())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8061)


