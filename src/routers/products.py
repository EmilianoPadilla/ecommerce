from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.products import ProductDB
from src.models.users import UserDB
from src.schemas.products import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
from src.database.database import get_db
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])


def product_to_response(product: ProductDB, db: Session) -> ProductResponse:
    owner_username = None
    if product.owner_id:
        owner = db.query(UserDB).filter(UserDB.id == product.owner_id).first()
        if owner:
            owner_username = owner.username

    return ProductResponse(
        id=product.id,
        name=product.name,
        price=product.price,
        stock=product.stock,
        image_url=product.image_url,
        owner_username=owner_username
    )


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
    return [product_to_response(p, db) for p in products]


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

    return product_to_response(product, db)


##################   POST   #########################

@router.post("/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
    )
def create_product(
    item: ProductCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)  # must be logged in
):
    try:
        product_data = item.model_dump()
        product_data["owner_id"] = current_user.id  # set owner automatically

        new_product = ProductDB(**product_data)

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return product_to_response(new_product, db)

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
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
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

        if product.owner_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own products!"
            )

        update_data = item.model_dump()

        for key, value in update_data.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)

        return product_to_response(product, db)

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
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
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

        if product.owner_id and product.owner_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own products!"
            )

        update_data = item.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)

        return product_to_response(product, db)

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
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
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

        if product.owner_id and product.owner_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only delete your own products!"
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