from datetime import date, timedelta
from models.room import PricePeriod
from sqlalchemy.orm import Session
from fastapi import  HTTPException


from datetime import date, timedelta
from typing import List
from models.room import PricePeriod
from sqlalchemy.orm import Session
from fastapi import HTTPException

def calculate_booking_price(
    room_id: int,
    check_in: date,
    check_out: date,
    number_of_guests: int,
    db: Session
) -> float:
    """
    Рассчитывает стоимость бронирования с учётом количества гостей.
    Если для указанного количества гостей нет ценового периода,
    используется период с ближайшим большим количеством гостей.
    """
    # Получаем все периоды для комнаты, которые пересекаются с датами бронирования
    # и имеют количество гостей >= запрошенного
    price_periods = db.query(PricePeriod).filter(
        PricePeriod.room_id == room_id,
        PricePeriod.number_of_guests >= number_of_guests,
        PricePeriod.end_date >= check_in,
        PricePeriod.start_date <= check_out - timedelta(days=1)
    ).order_by(PricePeriod.number_of_guests.asc()).all()

    if not price_periods:
        # Если вообще нет подходящих периодов
        raise HTTPException(
            status_code=400,
            detail=f"Не найдено цен для {number_of_guests} гостей. Создайте цены на эти даты."
        )

    total_price = 0.0
    current_date = check_in
    
    # Перебираем каждый день бронирования
    while current_date < check_out:
        best_price = None
        best_period = None
        
        # Ищем лучший ценовой период для текущего дня
        for period in price_periods:
            if period.start_date <= current_date <= period.end_date:
                # Если нашли период для точного количества гостей - используем его сразу
                if period.number_of_guests == number_of_guests:
                    best_period = period
                    break
                
                # Иначе ищем период с минимальным бóльшим количеством гостей
                if best_price is None or period.number_of_guests < best_period.number_of_guests:
                    best_price = period.price
                    best_period = period
        
        if best_period is None:
            raise HTTPException(
                status_code=400,
                detail=f"Цена на эту дату не найдена {current_date} для  {number_of_guests} гостей"
            )
        
        total_price += best_period.price
        current_date += timedelta(days=1)
    
    return total_price