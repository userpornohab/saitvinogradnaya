from fastapi import APIRouter, Depends, HTTPException, status, Query  
from sqlalchemy.orm import Session
from typing import List,  Optional
from sqlalchemy import func, and_
from models.user import User
from datetime import date, timedelta

from database.database import get_db
from models.room import Booking, CalendarSyncEvent, Room
from schemas.room import BookingCreate, BookingResponse, BookingUpdate, BookingBase
from auth.dependencies import check_superuser
from utils.availability import is_room_available_for_period
from utils.ical_sync import is_blocking_calendar_period
from utils.price_calculator import calculate_booking_price

router = APIRouter(prefix="/bookings", tags=["bookings"])

def _overlap_nights(booking: Booking, start_date: date, end_date: date) -> int:
    start = max(booking.check_in_date, start_date)
    end = min(booking.check_out_date, end_date + timedelta(days=1))
    return max((end - start).days, 0)

def _overlap_income(booking: Booking, start_date: date, end_date: date) -> float:
    booking_nights = max((booking.check_out_date - booking.check_in_date).days, 0)
    if booking_nights == 0:
        return 0.0
    return float(booking.price) / booking_nights * _overlap_nights(booking, start_date, end_date)

def _period_stats(bookings: List[Booking], start_date: date, end_date: date, rooms_count: int) -> dict:
    total_bookings = len(bookings)
    total_income = sum(_overlap_income(booking, start_date, end_date) for booking in bookings)
    total_guests = sum(booking.number_of_guests for booking in bookings)
    total_nights = sum(_overlap_nights(booking, start_date, end_date) for booking in bookings)
    total_capacity_nights = max(((end_date - start_date).days + 1) * rooms_count, 0)
    occupancy_rate = (total_nights / total_capacity_nights * 100) if total_capacity_nights else 0

    return {
        "total_bookings": total_bookings,
        "total_income": float(total_income),
        "total_guests": total_guests,
        "total_nights": total_nights,
        "avg_duration": round(total_nights / total_bookings, 1) if total_bookings else 0,
        "avg_check": round(float(total_income) / total_bookings, 2) if total_bookings else 0,
        "occupancy_rate": round(occupancy_rate, 1),
        "capacity_nights": total_capacity_nights
    }

def _percent_change(current: float, previous: float) -> Optional[float]:
    if previous == 0:
        return None if current else 0
    return round((current - previous) / previous * 100, 1)

def _month_key(value: date) -> str:
    return value.strftime("%Y-%m")

def _next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)

def _monthly_income(bookings: List[Booking], start_date: date, end_date: date) -> List[dict]:
    month_totals = {}
    current_month = date(start_date.year, start_date.month, 1)
    last_month = date(end_date.year, end_date.month, 1)

    while current_month <= last_month:
        month_totals[_month_key(current_month)] = 0.0
        current_month = _next_month(current_month)

    for booking in bookings:
        booking_nights = max((booking.check_out_date - booking.check_in_date).days, 0)
        if booking_nights == 0:
            continue

        price_per_night = float(booking.price) / booking_nights
        current = max(booking.check_in_date, start_date)
        booking_end = min(booking.check_out_date, end_date + timedelta(days=1))

        while current < booking_end:
            month_start = date(current.year, current.month, 1)
            month_end = min(_next_month(month_start), booking_end)
            nights = max((month_end - current).days, 0)
            month_totals[_month_key(month_start)] = month_totals.get(_month_key(month_start), 0.0) + price_per_night * nights
            current = month_end

    return [
        {"month": month, "income": round(income, 2)}
        for month, income in sorted(month_totals.items())
    ]

def _monthly_occupancy(bookings: List[Booking], start_date: date, end_date: date, rooms_count: int) -> List[dict]:
    month_nights = {}
    month_capacity = {}
    current_month = date(start_date.year, start_date.month, 1)
    last_month = date(end_date.year, end_date.month, 1)

    while current_month <= last_month:
        next_month = _next_month(current_month)
        period_start = max(current_month, start_date)
        period_end = min(next_month, end_date + timedelta(days=1))
        days_in_period = max((period_end - period_start).days, 0)
        key = _month_key(current_month)
        month_nights[key] = 0
        month_capacity[key] = days_in_period * rooms_count
        current_month = next_month

    for booking in bookings:
        current = max(booking.check_in_date, start_date)
        booking_end = min(booking.check_out_date, end_date + timedelta(days=1))

        while current < booking_end:
            month_start = date(current.year, current.month, 1)
            month_end = min(_next_month(month_start), booking_end)
            nights = max((month_end - current).days, 0)
            key = _month_key(month_start)
            month_nights[key] = month_nights.get(key, 0) + nights
            current = month_end

    return [
        {
            "month": month,
            "occupancy_rate": round(month_nights[month] / month_capacity[month] * 100, 1) if month_capacity[month] else 0,
            "occupied_nights": month_nights[month],
            "capacity_nights": month_capacity[month]
        }
        for month in sorted(month_capacity.keys())
    ]
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

    room = db.query(Room).get(booking.room_id)
    if not is_room_available_for_period(
        db=db,
        room=room,
        check_in_date=booking_data.check_in_date,
        check_out_date=booking_data.check_out_date,
        exclude_booking_id=booking_id,
    ):
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

    if not is_room_available_for_period(
        db=db,
        room=room,
        check_in_date=booking_data.check_in_date,
        check_out_date=booking_data.check_out_date,
    ):
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
    
    bookings = db.query(Booking).filter(Booking.room_id == room_id).all()
    external_events = db.query(CalendarSyncEvent).filter(CalendarSyncEvent.room_id == room_id).all()

    busy_periods = list(bookings)
    for event in external_events:
        if not is_blocking_calendar_period(event.summary or "", event.start_date, event.end_date):
            continue
        for _ in range(max(room.number_of_rooms or 1, 1)):
            busy_periods.append({
                "room_id": event.room_id,
                "check_in_date": event.start_date,
                "check_out_date": event.end_date,
            })

    return busy_periods


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
    
    rooms_query = db.query(Room)
    if room_id is not None:
        rooms_query = rooms_query.filter(Room.id == room_id)
    rooms_count = sum(room.number_of_rooms for room in rooms_query.all())

    period_days = (end_date - start_date).days + 1
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - timedelta(days=period_days - 1)

    previous_query = db.query(Booking).filter(
        and_(
            Booking.check_in_date <= previous_end,
            Booking.check_out_date >= previous_start
        )
    )
    if room_id is not None:
        previous_query = previous_query.filter(Booking.room_id == room_id)

    bookings_in_period = query.all()
    previous_bookings = previous_query.all()
    
    statistics = _period_stats(bookings_in_period, start_date, end_date, rooms_count)
    previous_statistics = _period_stats(previous_bookings, previous_start, previous_end, rooms_count)

    monthly_income = _monthly_income(bookings_in_period, start_date, end_date)
    monthly_occupancy = _monthly_occupancy(bookings_in_period, start_date, end_date, rooms_count)
    
    # Дополнительная статистика по комнатам
    room_stats = []
    if room_id is None:  # Только если не фильтруем по конкретной комнате
        bookings_by_room = {}
        for booking in bookings_in_period:
            stats = bookings_by_room.setdefault(booking.room_id, {
                "booking_count": 0,
                "total_income": 0,
                "total_guests": 0,
                "total_nights": 0
            })
            stats["booking_count"] += 1
            stats["total_income"] += _overlap_income(booking, start_date, end_date)
            stats["total_guests"] += booking.number_of_guests
            stats["total_nights"] += _overlap_nights(booking, start_date, end_date)

        all_rooms = db.query(Room).order_by(Room.id).all()
        period_capacity_days = (end_date - start_date).days + 1

        for room in all_rooms:
            stats = bookings_by_room.get(room.id, {
                "booking_count": 0,
                "total_income": 0,
                "total_guests": 0,
                "total_nights": 0
            })
            capacity_nights = period_capacity_days * room.number_of_rooms
            room_stats.append({
                "room_id": room.id,
                "room_title": room.title,
                "booking_count": stats["booking_count"],
                "total_income": float(stats["total_income"]),
                "total_guests": stats["total_guests"],
                "total_nights": stats["total_nights"],
                "occupancy_rate": round(stats["total_nights"] / capacity_nights * 100, 1) if capacity_nights else 0,
                "avg_check": round(stats["total_income"] / stats["booking_count"], 2) if stats["booking_count"] else 0,
                "avg_duration": round(stats["total_nights"] / stats["booking_count"], 1) if stats["booking_count"] else 0,
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
        "statistics": statistics,
        "previous_period": {
            "start_date": previous_start,
            "end_date": previous_end,
            "statistics": previous_statistics,
            "changes": {
                "bookings_percent": _percent_change(statistics["total_bookings"], previous_statistics["total_bookings"]),
                "income_percent": _percent_change(statistics["total_income"], previous_statistics["total_income"]),
                "guests_percent": _percent_change(statistics["total_guests"], previous_statistics["total_guests"]),
                "occupancy_percent": _percent_change(statistics["occupancy_rate"], previous_statistics["occupancy_rate"])
            }
        },
        "monthly_income": monthly_income,
        "monthly_occupancy": monthly_occupancy,
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
