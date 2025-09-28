from fastapi import APIRouter, Depends, HTTPException, status, Query  
from sqlalchemy.orm import Session
from typing import List,  Optional
from sqlalchemy import func, and_
from models.user import User
from datetime import date

from database.database import get_db
from models.room import Booking, Room
from schemas.room import BookingCreate, BookingResponse, BookingUpdate, BookingBase
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


@router.get("/booking-stats")
async def get_booking_statistics(
    start_date: date = Query(..., description="Начальная дата периода (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Конечная дата периода (YYYY-MM-DD)"),
    room_id: Optional[int] = Query(None, description="ID комнаты (опционально)"),
    db: Session = Depends(get_db)
):
    """
    Получить статистику по бронированиям за указанный период
    """
    # Проверка валидности дат
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Начальная дата не может быть больше конечной")
    
    # Базовый запрос с фильтром по датам
    query = db.query(Booking).filter(
        and_(
            Booking.check_in_date <= end_date,
            Booking.check_out_date >= start_date
        )
    )
    
    # Фильтр по комнате если указан room_id
    if room_id is not None:
        query = query.filter(Booking.room_id == room_id)
    
    # Получаем все бронирования за период
    bookings_in_period = query.all()
    
    # Рассчитываем статистику
    total_bookings = len(bookings_in_period)
    total_income = sum(booking.price for booking in bookings_in_period)
    total_guests = sum(booking.number_of_guests for booking in bookings_in_period)
    
    # Дополнительная статистика по комнатам
    room_stats = []
    if room_id is None:  # Только если не фильтруем по конкретной комнате
        # Группируем по комнатам
        room_query = db.query(
            Booking.room_id,
            Room.title,
            func.count(Booking.id).label('booking_count'),
            func.sum(Booking.price).label('total_income'),
            func.sum(Booking.number_of_guests).label('total_guests')
        ).join(Room).filter(
            and_(
                Booking.check_in_date <= end_date,
                Booking.check_out_date >= start_date
            )
        ).group_by(Booking.room_id, Room.title)
        
        room_stats_data = room_query.all()
        
        for room_stat in room_stats_data:
            room_stats.append({
                "room_id": room_stat.room_id,
                "room_title": room_stat.title,
                "booking_count": room_stat.booking_count or 0,
                "total_income": float(room_stat.total_income or 0),
                "total_guests": room_stat.total_guests or 0
            })
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "filter": {
            "room_id": room_id,
            "room_title": db.query(Room.title).filter(Room.id == room_id).scalar() if room_id else "Все комнаты"
        },
        "statistics": {
            "total_bookings": total_bookings,
            "total_income": float(total_income),
            "total_guests": total_guests
        },
        "room_statistics": room_stats if room_id is None else None
    }

# Дополнительный эндпоинт для более детальной статистики
@router.get("/booking-detailed-stats")
async def get_detailed_booking_statistics(
    start_date: date = Query(..., description="Начальная дата периода (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Конечная дата периода (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Детальная статистика по бронированиям с разбивкой по дням
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Начальная дата не может быть больше конечной")
    
    # Статистика по дням
    daily_stats_query = db.query(
        Booking.check_in_date,
        func.count(Booking.id).label('bookings_count'),
        func.sum(Booking.price).label('daily_income'),
        func.sum(Booking.number_of_guests).label('daily_guests')
    ).filter(
        and_(
            Booking.check_in_date >= start_date,
            Booking.check_in_date <= end_date
        )
    ).group_by(Booking.check_in_date)
    
    daily_stats = []
    for stat in daily_stats_query.all():
        daily_stats.append({
            "date": stat.check_in_date,
            "bookings_count": stat.bookings_count,
            "daily_income": float(stat.daily_income or 0),
            "daily_guests": stat.daily_guests or 0
        })
    
    # Статистика по комнатам
    room_stats_query = db.query(
        Room.id,
        Room.title,
        func.count(Booking.id).label('bookings_count'),
        func.sum(Booking.price).label('total_income'),
        func.avg(Booking.price).label('avg_income_per_booking'),
        func.sum(Booking.number_of_guests).label('total_guests')
    ).join(Booking).filter(
        and_(
            Booking.check_in_date <= end_date,
            Booking.check_out_date >= start_date
        )
    ).group_by(Room.id, Room.title)
    
    room_stats = []
    for stat in room_stats_query.all():
        room_stats.append({
            "room_id": stat.id,
            "room_title": stat.title,
            "bookings_count": stat.bookings_count or 0,
            "total_income": float(stat.total_income or 0),
            "avg_income_per_booking": float(stat.avg_income_per_booking or 0),
            "total_guests": stat.total_guests or 0
        })
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "daily_statistics": daily_stats,
        "room_statistics": room_stats
    }