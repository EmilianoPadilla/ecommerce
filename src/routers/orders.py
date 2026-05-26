from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.orders import OrderDB
from src.models.users import UserDB
from src.schemas.orders import OrderCreate, OrderUpdate, OrderResponse
from src.database.database import get_db
from src.auth.dependencies import get_current_user


router = APIRouter(prefix="/orders", tags=["Orders"])


##################   GET ALL   #########################

@router.get("/", response_model=list[OrderResponse])
def get_orders(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    orders = (
        db.query(OrderDB)
        .filter(OrderDB.user_id == current_user.id)
        .order_by(OrderDB.id)
        .limit(limit)
        .offset(offset)
        .all()
    )
    return orders


##################   GET ONE   #########################

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    order = (
        db.query(OrderDB)
        .filter(OrderDB.id == order_id)
        .first()
    )

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

    return order


##################   POST   #########################

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    item: OrderCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    try:
        new_order = OrderDB(
            **item.model_dump(),
            user_id=current_user.id
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        return new_order

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid order data"
        )
    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


##################   PUT   #########################

@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    item: OrderCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    try:
        order = db.query(OrderDB).filter(
            OrderDB.id == order_id
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

        update_data = item.model_dump()

        for key, value in update_data.items():
            setattr(order, key, value)

        db.commit()
        db.refresh(order)

        return order

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid order data"
        )
    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


##################   PATCH   #########################

@router.patch("/{order_id}", response_model=OrderResponse)
def update_order_partial(
    order_id: int,
    item: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    try:
        order = db.query(OrderDB).filter(
            OrderDB.id == order_id
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

        update_data = item.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(order, key, value)

        db.commit()
        db.refresh(order)

        return order

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid order data"
        )
    
    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


##################   DELETE   #########################

@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    try:
        order = db.query(OrderDB).filter(
            OrderDB.id == order_id
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

        db.delete(order)
        db.commit()

        return {"message": "Order deleted successfully!"}

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
