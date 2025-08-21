from fastapi import APIRouter, Depends, HTTPException, status, Query  
from sqlalchemy.orm import Session
from typing import List,  Optional
from models.user import User
from database.database import get_db
from models.room import Booking, Room, PricePeriod
from schemas.room import BookingCreate, BookingResponse, BookingUpdate,BookingClientData, BookingBase
from auth.dependencies import check_superuser
from utils.price_calculator import calculate_booking_price

router = APIRouter(prefix="/bookings", tags=["bookings"])
@router.patch("/{booking_id}", response_model=BookingResponse, dependencies=[Depends(check_superuser)])
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_superuser)
):
    # Только суперпользователь может изменять бронирования
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to modify bookings")
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if not current_user.is_superuser and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this booking")

    if booking_data.check_out_date <= booking_data.check_in_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date"
        )

    overlapping = db.query(Booking).filter(
        Booking.room_id == booking.room_id,
        Booking.id != booking_id,
        Booking.check_in_date < booking_data.check_out_date,
        Booking.check_out_date > booking_data.check_in_date
    ).count()

    room = db.query(Room).get(booking.room_id)
    if overlapping >= room.number_of_rooms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is already booked for these dates"
        )

    booking.check_in_date = booking_data.check_in_date
    booking.check_out_date = booking_data.check_out_date
    booking.number_of_guests = booking_data.number_of_guests  # Обновляем количество гостей

    if booking_data.guest_name is not None:
        booking.guest_name = booking_data.guest_name
    if booking_data.guest_phone is not None:
        booking.guest_phone = booking_data.guest_phone
    if booking_data.guest_comment is not None:
        booking.guest_comment = booking_data.guest_comment

    if booking.price != booking_data.price:
        booking.price = booking_data.price
    else:
        try:
            # Используем новую функцию с учётом количества гостей
            booking_data.price = calculate_booking_price(
                room_id=booking.room_id,
                check_in=booking_data.check_in_date,
                check_out=booking_data.check_out_date,
                number_of_guests=booking_data.number_of_guests,  # Добавляем количество гостей
                db=db
            )
            booking.price = booking_data.price
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(500, detail=f"Price calculation failed: {str(e)}")
    
    db.commit()
    db.refresh(booking)
    return booking
# Шаг 1: Создание бронирования без персональных данных
@router.post("/", response_model=BookingResponse, dependencies=[Depends(check_superuser)])
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
):
    # Валидация данных и создание бронирования
    if booking_data.number_of_guests is None:
        booking_data.number_of_guests = 1
    
    if booking_data.number_of_guests < 1:
        raise HTTPException(400, detail="Number of guests must be at least 1")
    
    room = db.query(Room).filter(Room.id == booking_data.room_id).first()
    if not room:
        raise HTTPException(404, detail="Room not found")
    
    # Расчет цены
    if booking_data.price is None:
        try:
            booking_data.price = calculate_booking_price(
                room_id=booking_data.room_id,
                check_in=booking_data.check_in_date,
                check_out=booking_data.check_out_date,
                number_of_guests=booking_data.number_of_guests,
                db=db
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(500, detail=f"Price calculation failed: {str(e)}")
    
    elif booking_data.price <= 0:
        raise HTTPException(400, detail="Price must be positive")

    # Проверка дат
    if booking_data.check_out_date <= booking_data.check_in_date:
        raise HTTPException(400, detail="Invalid dates")

    # Проверка доступности
    overlapping_bookings = db.query(Booking).filter(
        Booking.room_id == booking_data.room_id,
        Booking.check_in_date < booking_data.check_out_date,
        Booking.check_out_date > booking_data.check_in_date
    ).count()
    
    if overlapping_bookings >= room.number_of_rooms:
        raise HTTPException(400, detail="На этот период все комнаты заняты")


    # Создаем бронирование без персональных данных
    booking_dict = booking_data.dict()
    db_booking = Booking(**booking_dict)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking


@router.get("/admin", response_model=List[BookingResponse], dependencies=[Depends(check_superuser)])
def get_all_bookings_admin(db: Session = Depends(get_db)):
    return db.query(Booking).all()


# В эндпоинте удаления бронирования
@router.delete("/{booking_id}", response_model=BookingResponse, dependencies=[Depends(check_superuser)])
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_superuser)

):
    # Только суперпользователь может удалять бронирования
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to delete bookings")
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    
    db.delete(booking)
    db.commit()
    return booking


@router.get("/rooms/{room_id}/admin", response_model=List[BookingResponse], dependencies=[Depends(check_superuser)])
def get_bookings_by_room_admin(
    room_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить все бронирования для указанной комнаты
    """
    # Проверяем существует ли комната
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Получаем все бронирования для этой комнаты
    bookings = db.query(Booking).filter(Booking.room_id == room_id).all()
    
    return bookings

@router.get("/rooms/{room_id}", response_model=List[BookingBase])
def get_bookings_by_room(
    room_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить все бронирования для указанной комнаты
    """
    # Проверяем существует ли комната
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Получаем все бронирования для этой комнаты
    bookings = db.query(Booking).filter(Booking.room_id == room_id).all()
    
    return bookings