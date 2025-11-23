from pydantic import BaseModel

class SyllableWithAudio(BaseModel):
    syllable: str
    audio_file: str

class PhenomeMappingResponse(BaseModel):
    phenome_data_answers: list[list[SyllableWithAudio]]
    phenome_data_options: list[list[SyllableWithAudio]]
    
