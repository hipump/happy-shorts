from typing import List, Optional
from pydantic import BaseModel, Field

class Word(BaseModel):
    word: str
    start: float
    end: float
    probability: float = 1.0

class Segment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    words: List[Word] = Field(default_factory=list)

class Transcript(BaseModel):
    language: str = "ko"
    duration: float
    segments: List[Segment] = Field(default_factory=list)

class Highlight(BaseModel):
    id: int = 1
    title: str = "하이라이트"
    hook_text: str = ""
    start_time: float
    end_time: float
    duration: float = 0.0
    reason: str = ""
    summary_points: List[str] = Field(default_factory=list)
    virality_score: int = 85
    score_breakdown: dict = Field(default_factory=dict)

    def model_post_init(self, __context):
        if self.duration == 0.0:
            self.duration = round(self.end_time - self.start_time, 2)

class VideoMetadata(BaseModel):
    source: str
    is_url: bool
    title: str
    duration: float
    width: int = 1920
    height: int = 1080
    fps: float = 30.0
    local_path: str
