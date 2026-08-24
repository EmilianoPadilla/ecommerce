from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.models.cart import CartItemDB
from src.models.products import ProductDB
from src.models.users import UserDB
from src.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartItemWithProduct
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=list[CartItemWithProduct])
def get_cart(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart_items = db.query(CartItemDB).filter(
        CartItemDB.user_id == current_user.id
    ).all()

    result = []
    for item in cart_items:
        product = db.query(ProductDB).filter(
            ProductDB.id == item.product_id
        ).first()
        result.append(CartItemWithProduct(
            id=item.id,
            user_id=item.user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            product_name=product.name,
            product_price=product.price,
            product_image_url=product.image_url
        ))
    return result


@router.post("/", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item: CartItemCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # check if product exists
    product = db.query(ProductDB).filter(
        ProductDB.id == item.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # check if item already in cart
    existing = db.query(CartItemDB).filter(
        CartItemDB.user_id == current_user.id,
        CartItemDB.product_id == item.product_id
    ).first()

    if existing:
        existing.quantity += item.quantity
        db.commit()
        db.refresh(existing)
        return existing

    new_item = CartItemDB(
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.patch("/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    item: CartItemUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart_item = db.query(CartItemDB).filter(
        CartItemDB.id == item_id,
        CartItemDB.user_id == current_user.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if item.quantity is not None:
        if item.quantity <= 0:
            db.delete(cart_item)
            db.commit()
            return cart_item
        cart_item.quantity = item.quantity

    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.delete("/{item_id}")
def remove_from_cart(
    item_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart_item = db.query(CartItemDB).filter(
        CartItemDB.id == item_id,
        CartItemDB.user_id == current_user.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("/")
def clear_cart(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(CartItemDB).filter(
        CartItemDB.user_id == current_user.id
    ).delete()
    db.commit()
    return {"message": "Cart cleared"}