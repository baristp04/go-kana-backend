from fastapi import FastAPI
from app.api.kana import kana_router
from app.api.quiz import quiz_router

app = FastAPI(title="Go-Kana Backend API")

app.include_router(kana_router, prefix="/api/kana", tags=["Kana Alphabets"])
app.include_router(quiz_router, prefix="/api/quiz", tags=["Quiz System"])

@app.get("/")
def root_check():
    return {"message": "Go-Kana Backend API is running!"}