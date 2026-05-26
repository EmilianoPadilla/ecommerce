from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.models.users import UserDB
from src.auth.hashing import verify_password
from src.auth.jwt_handler import create_access_token

router = APIRouter(tags=["Auth"])


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(UserDB).filter(
        UserDB.email == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        {"user_id": user.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
