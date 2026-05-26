from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.users import UserDB
from src.schemas.users import UserCreate, UserUpdate, UserResponse
from src.database.database import get_db
from src.auth.hashing import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


##################   GET ALL   #########################

@router.get("/", response_model=list[UserResponse])
def get_users(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    users = (
        db.query(UserDB)
        .order_by(UserDB.id)
        .limit(limit)
        .offset(offset)
        .all()
    )
    return users


##################   GET ONE   #########################

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = (
        db.query(UserDB)
        .filter(UserDB.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found!"
        )

    return user


##################   POST   #########################

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    item: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        user_data = item.model_dump()
        user_data["password"] = hash_password(user_data["password"])

        new_user = UserDB(**user_data)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Duplicate or invalid data"
        )
    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


##################   PUT   #########################

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    item: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        user = db.query(UserDB).filter(
            UserDB.id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found!"
            )

        update_data = item.model_dump()

        if "password" in update_data:
            update_data["password"] = hash_password(
                update_data["password"]
            )

        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)

        return user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Duplicate or invalid data"
        )
    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


##################   PATCH   #########################

@router.patch("/{user_id}", response_model=UserResponse)
def update_user_partial(
    user_id: int,
    item: UserUpdate,
    db: Session = Depends(get_db)
):
    try:
        user = db.query(UserDB).filter(
            UserDB.id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found!"
            )

        update_data = item.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["password"] = hash_password(
                update_data["password"]
            )

        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)

        return user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Duplicate or invalid data"
        )
    
    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


##################   DELETE   #########################

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        user = db.query(UserDB).filter(
            UserDB.id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found!"
            )

        db.delete(user)
        db.commit()

        return {"message": "User deleted successfully!"}

    except HTTPException:
        raise
    
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
