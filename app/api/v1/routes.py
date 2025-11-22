from fastapi import APIRouter

# Import all route modules
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
from app.services.Adult.word_parts_workshop.word_parts_workshop_route import router as word_parts_workshop_router
from app.services.Adult.sentence_builder.sentence_builder_route import router as sentence_builder_router

# Create main API router
api_router = APIRouter()

# Include all routers with v1 prefix and appropriate tags
api_router.include_router(writing_router, prefix="/writing", tags=["writing"])

api_router.include_router(sight_word_router, prefix="/reading/sight-word-practice", tags=["reading"])
api_router.include_router(reading_comprehension_router, prefix="/reading/comprehension", tags=["reading"])
api_router.include_router(phoneme_flashcards_router, prefix="/reading/phoneme-flashcards", tags=["reading"])

api_router.include_router(power_words_router, prefix="/presentation/power-words", tags=["presentation"])
api_router.include_router(flow_chain_router, prefix="/presentation/flow-chain", tags=["presentation"])
api_router.include_router(context_spin_router, prefix="/presentation/context-spin", tags=["presentation"])
api_router.include_router(precision_drill_router, prefix="/presentation/precision-drill", tags=["presentation"])

api_router.include_router(listen_speak_router, prefix="/speaking/listen-speak", tags=["speaking"])
api_router.include_router(phrase_repeat_router, prefix="/speaking/phrase-repeat", tags=["speaking"])
api_router.include_router(pronunciation_router, prefix="/speaking/pronunciation", tags=["speaking"])
api_router.include_router(vocabulary_challenge_router, prefix="/speaking/vocabulary-challenge", tags=["speaking"])

api_router.include_router(word_flash_router, prefix="/adult/word-flash", tags=["adult"])
api_router.include_router(word_parts_workshop_router, prefix="/adult/word-parts-workshop", tags=["adult"])
api_router.include_router(sentence_builder_router, prefix="/adult/sentence-builder", tags=["adult"])