from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.orderitems import OrderItemDB
from src.models.orders import OrderDB
from src.models.users import UserDB
from src.schemas.orderitems import (
    OrderItemCreate,
    OrderItemUpdate,
    OrderItemResponse
)
from src.database.database import get_db
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/orderitems", tags=["Orderitems"])


##################   GET ALL   #########################

@router.get("/", response_model=list[OrderItemResponse])
def get_orderitems(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    orderitems = (
        db.query(OrderItemDB)
        .join(OrderDB)
        .filter(OrderDB.user_id == current_user.id)
        .order_by(OrderItemDB.id)
        .limit(limit)
        .offset(offset)
        .all()
    )
    return orderitems


##################   GET ONE   #########################

@router.get("/{orderitem_id}", response_model=OrderItemResponse)
def get_orderitem(
    orderitem_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    orderitem = db.query(OrderItemDB).filter(
        OrderItemDB.id == orderitem_id
    ).first()

    if not orderitem:
        raise HTTPException(
            status_code=404,
            detail="Order item not found!"
        )

    if orderitem.order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    return orderitem


##################   POST   #########################

@router.post(
    "/",
    response_model=OrderItemResponse,
    status_code=status.HTTP_201_CREATED
)
def create_orderitem(
    item: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    try:
        order = db.query(OrderDB).filter(
            OrderDB.id == item.order_id
        ).first()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found!"
            )

        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Forbidden"
            )

        new_orderitem = OrderItemDB(**item.model_dump())

        db.add(new_orderitem)
        db.commit()
        db.refresh(new_orderitem)

        return new_orderitem

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid order item data"
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

@router.patch("/{orderitem_id}", response_model=OrderItemResponse)
def update_orderitem_partial(
    orderitem_id: int,
    item: OrderItemUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    try:
        orderitem = db.query(OrderItemDB).filter(
            OrderItemDB.id == orderitem_id
        ).first()

        if not orderitem:
            raise HTTPException(
                status_code=404,
                detail="Order item not found!"
            )

        if orderitem.order.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Forbidden"
            )

        update_data = item.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(orderitem, key, value)

        db.commit()
        db.refresh(orderitem)

        return orderitem

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid order item data"
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

@router.delete("/{orderitem_id}")
def delete_orderitem(
    orderitem_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    try:
        orderitem = db.query(OrderItemDB).filter(
            OrderItemDB.id == orderitem_id
        ).first()

        if not orderitem:
            raise HTTPException(
                status_code=404,
                detail="Order item not found!"
            )

        if orderitem.order.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Forbidden"
            )

        db.delete(orderitem)
        db.commit()

        return {"message": "Order item deleted successfully!"}

    except HTTPException:
        raise
    
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
