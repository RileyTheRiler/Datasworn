from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import List, Optional
from src.practice_cards import PracticeManager

practice_manager = PracticeManager()

router = APIRouter(prefix="/api/practice", tags=["practice"])

class CustomSetRequest(BaseModel):
    title: str
    difficulty: str
    cards: List[str]

class TrackUsageRequest(BaseModel):
    card_id: str
    is_recording: bool
    time_ms: int

@router.get("/sets")
async def get_sets():
    sets = practice_manager.get_all_sets()
    return {"sets": [s.to_dict() for s in sets]}

@router.get("/sets/{set_id}")
async def get_set(set_id: str):
    s = practice_manager.get_set(set_id)
    if not s:
        raise HTTPException(status_code=404, detail="Set not found")
    return s.to_dict()

@router.post("/sets")
async def create_set(req: CustomSetRequest):
    new_set = practice_manager.add_custom_set(req.title, req.difficulty, req.cards)
    return new_set.to_dict()

@router.get("/progress")
async def get_progress():
    return practice_manager.progress.to_dict()

@router.post("/track")
async def track_usage(req: TrackUsageRequest):
    practice_manager.track_usage(req.card_id, req.is_recording, req.time_ms)
    return {"status": "ok"}

def register_practice_routes(app: FastAPI):
    app.include_router(router)
