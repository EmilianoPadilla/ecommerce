from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.database.database import get_db
from .models.users import UserDB
from .auth.jwt_handler import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = verify_token(token)
        user_id = payload.get("user_id")

        user = db.query(UserDB).filter(UserDB.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")

        return user

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
