from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.products import ProductDB
from src.schemas.products import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
from src.database.database import get_db

router = APIRouter(prefix="/products", tags=["Products"])


##################   GET ALL   #########################

@router.get("/", response_model=list[ProductResponse])
def get_products(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    products = (
        db.query(ProductDB)
        .order_by(ProductDB.id)
        .limit(limit)
        .offset(offset)
        .all()
    )
    return products


##################   GET ONE   #########################

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = (
        db.query(ProductDB)
        .filter(ProductDB.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found!"
        )

    return product


##################   POST   #########################

@router.post("/", 
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
    )
def create_product(
    item: ProductCreate,
    db: Session = Depends(get_db)
):
    try:
        new_product = ProductDB(**item.model_dump())

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid foreign key or duplicate value"
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

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    item: ProductCreate,
    db: Session = Depends(get_db)
):
    try:
        product = (
            db.query(ProductDB)
            .filter(ProductDB.id == product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found!"
            )

        update_data = item.model_dump()

        for key, value in update_data.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)

        return product

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid foreign key or duplicate value"
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

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product_partial(
    product_id: int,
    item: ProductUpdate,
    db: Session = Depends(get_db)
):
    try:
        product = (
            db.query(ProductDB)
            .filter(ProductDB.id == product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found!"
            )

        update_data = item.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)

        return product

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid foreign key or duplicate value"
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

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    try:
        product = (
            db.query(ProductDB)
            .filter(ProductDB.id == product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found!"
            )

        db.delete(product)
        db.commit()

        return {"message": "Product deleted successfully!"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid foreign key or duplicate value"
        )


    except HTTPException:
        raise
    
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
