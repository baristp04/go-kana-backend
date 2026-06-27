import json
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException

kana_router = APIRouter()

# Determine the base directory to safely locate the 'data' folder
# This goes up two levels from the current file's location to reach the root.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

def load_json(filename: str):
    file_path = DATA_DIR / filename
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {filename} not found! Please check the data directory.")
        return []

# Load data into memory (RAM) at startup for fast access
KANA_DB = {
    "hiragana": {
        "basic": load_json("basic-hiragana.json"),
        "combinations": load_json("hiragana.json")
    },
    "katakana": {
        "basic": load_json("basic-katakana.json"),
        "combinations": load_json("katakana.json")
    }
}

@kana_router.get("/")
def get_kana_data(
    alphabet: str = Query(..., description="Must be 'hiragana' or 'katakana'"),
    combinations: bool = Query(False, description="Include combinations? (true/false)")
):
    if alphabet not in KANA_DB:
        raise HTTPException(
            status_code=400, 
            detail="Invalid alphabet. Please use 'hiragana' or 'katakana'."
        )
    
    category = "combinations" if combinations else "basic"
    
    return {"data": KANA_DB[alphabet][category]}