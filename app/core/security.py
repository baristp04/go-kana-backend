import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CREDENTIALS_PATH = BASE_DIR / "data" / "firebase-credentials.json"

cred = credentials.Certificate(str(CREDENTIALS_PATH))

db_url = os.getenv("FIREBASE_DATABASE_URL")

if not db_url:
    raise ValueError("HATA: .env dosyasında FIREBASE_DATABASE_URL bulunamadı!")

firebase_admin.initialize_app(cred, {
    'databaseURL': db_url
})

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:

        decoded_token = auth.verify_id_token(token)
        return decoded_token.get("uid")
        
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed.",
            headers={"WWW-Authenticate": "Bearer"},
        )