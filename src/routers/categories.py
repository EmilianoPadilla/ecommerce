from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.categories import CategoryDB
from src.schemas.categories import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)
from src.database.database import get_db

from src.models.products import ProductDB
from src.schemas.products import ProductResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


##################   GET ALL   #########################

@router.get("/", response_model=list[CategoryResponse])
def get_categories(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    categories = (
        db.query(CategoryDB)
        .order_by(CategoryDB.id)
        .limit(limit)
        .offset(offset)
        .all()
    )
    return categories


##################   GET ONE   #########################

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = (
        db.query(CategoryDB)
        .filter(CategoryDB.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found!"
        )

    return category

##################   GET PRODUCTS BY CATEGORY   #########################

@router.get("/{category_id}/products", response_model=list[ProductResponse])
def get_products_by_category(
    category_id: int,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    category = db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found!")
    
    products = (
        db.query(ProductDB)
        .filter(ProductDB.category_id == category_id)
        .order_by(ProductDB.id)
        .limit(limit)
        .offset(offset)
        .all()
    )
    
    from src.models.users import UserDB
    result = []
    for product in products:
        owner_username = None
        if product.owner_id:
            owner = db.query(UserDB).filter(UserDB.id == product.owner_id).first()
            if owner:
                owner_username = owner.username
        result.append(ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            stock=product.stock,
            image_url=product.image_url,
            owner_username=owner_username
        ))
    
    return result

##################   POST   #########################

@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(
    item: CategoryCreate,
    db: Session = Depends(get_db)
):
    try:
        new_category = CategoryDB(**item.model_dump())

        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return new_category

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

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    item: CategoryCreate,
    db: Session = Depends(get_db)
):
    try:
        category = (
            db.query(CategoryDB)
            .filter(CategoryDB.id == category_id)
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found!"
            )

        update_data = item.model_dump()

        for key, value in update_data.items():
            setattr(category, key, value)

        db.commit()
        db.refresh(category)

        return category

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

@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category_partial(
    category_id: int,
    item: CategoryUpdate,
    db: Session = Depends(get_db)
):
    try:
        category = (
            db.query(CategoryDB)
            .filter(CategoryDB.id == category_id)
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found!"
            )

        update_data = item.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(category, key, value)

        db.commit()
        db.refresh(category)

        return category

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

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    try:
        category = (
            db.query(CategoryDB)
            .filter(CategoryDB.id == category_id)
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found!"
            )

        db.delete(category)
        db.commit()

        return {"message": "Category deleted successfully!"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
