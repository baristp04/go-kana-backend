import random
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from firebase_admin import db
from app.core.security import get_current_user
from app.api.kana import KANA_DB  # Daha önce oluşturduğumuz veritabanını içe aktarıyoruz

quiz_router = APIRouter()

# --- Pydantic Models for Request Validation ---
class AnswerSubmit(BaseModel):
    alphabet: str           # "hiragana" or "katakana"
    combinations: bool      # true or false
    japanese: str           # e.g., "あ"
    user_answer: str        # e.g., "a"

@quiz_router.get("/generate")
def generate_question(
    alphabet: str = Query(..., description="Must be 'hiragana' or 'katakana'"),
    combinations: bool = Query(False, description="Include combinations?"),
    user_uid: str = Depends(get_current_user) 
):
    if alphabet not in KANA_DB:
        raise HTTPException(status_code=400, detail="Invalid alphabet.")
    
    category = "combinations" if combinations else "basic"
    data_list = KANA_DB[alphabet][category]
    
    if not data_list:
        raise HTTPException(status_code=404, detail="Data not found.")

    random_item = random.choice(data_list)
    
    return {
        "japanese": random_item["japanese"]
    }

@quiz_router.post("/submit")
def submit_answer(
    payload: AnswerSubmit,
    user_uid: str = Depends(get_current_user)
):
    if payload.alphabet not in KANA_DB:
        raise HTTPException(status_code=400, detail="Invalid alphabet.")

    category = "combinations" if payload.combinations else "basic"
    data_list = KANA_DB[payload.alphabet][category]
    correct_romaji = None

    for item in data_list:
        if item["japanese"] == payload.japanese:
            correct_romaji = item["romaji"]
            break
            
    if correct_romaji is None:
        raise HTTPException(status_code=404, detail="Character not found in database.")

    user_ref = db.reference(f'users/{user_uid}')
    
    user_data = user_ref.get() or {}
    current_streak = user_data.get('streak', 0)

    is_correct = (payload.user_answer.strip().lower() == correct_romaji.lower())

    if is_correct:
        new_streak = current_streak + 1
    else:
        new_streak = 0

    user_ref.update({
        'streak': new_streak
    })

    return {
        "is_correct": is_correct,
        "correct_answer": correct_romaji,
        "new_streak": new_streak
    }

@quiz_router.get("/streak")
def get_streak(user_uid: str = Depends(get_current_user)):
    user_ref = db.reference(f'users/{user_uid}')
    user_data = user_ref.get() or {}
    
    return {"streak": user_data.get('streak', 0)}

@quiz_router.post("/reset-streak")
def reset_streak(user_uid: str = Depends(get_current_user)):
    user_ref = db.reference(f'users/{user_uid}')
    user_ref.update({
        'streak': 0
    })
    
    return {"message": "Streak successfully reset.", "new_streak": 0}