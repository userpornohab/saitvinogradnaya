from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import extract
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from datetime import datetime

from database.database import get_db
from models.room import PricePeriod, Room
from schemas.room import PricePeriodResponse, PricePeriodCreate
from auth.dependencies import check_superuser

router = APIRouter(prefix="/price-periods", tags=["price-periods"])

@router.get("/", response_model=List[PricePeriodResponse])
def get_all_price_periods(db: Session = Depends(get_db)):
    return db.query(PricePeriod).all()

@router.get("/{period_id}", response_model=PricePeriodResponse)
def get_price_period(period_id: int, db: Session = Depends(get_db)):
    period = db.query(PricePeriod).get(period_id)
    if not period:
        raise HTTPException(404, "Price period not found")
    return period

@router.put("/{period_id}", response_model=PricePeriodResponse, dependencies=[Depends(check_superuser)])
def update_price_period(
    period_id: int, 
    period_data: PricePeriodCreate,
    db: Session = Depends(get_db)
):
    period = db.query(PricePeriod).get(period_id)
    if not period:
        raise HTTPException(404, "Price period not found")
    
    for field, value in period_data.dict().items():
        setattr(period, field, value)
    
    db.commit()
    db.refresh(period)
    return period

@router.delete("/{period_id}", response_model=PricePeriodResponse, dependencies=[Depends(check_superuser)])
def delete_price_period(period_id: int, db: Session = Depends(get_db)):
    period = db.query(PricePeriod).get(period_id)
    if not period:
        raise HTTPException(404, "Price period not found")
    
    db.delete(period)
    db.commit()
    return period

@router.post(
    "/rooms/{room_id}/price-periods", 
    response_model=PricePeriodResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_superuser)]
)
def create_price_period(
    room_id: int,
    period_data: PricePeriodCreate,
    db: Session = Depends(get_db)
):
    from models.room import Room
    room = db.query(Room).get(room_id)
    if not room:
        raise HTTPException(404, "Room not found")

    if period_data.start_date > period_data.end_date:
        raise HTTPException(422, "Start date cannot be after end date")

    # Фильтруем периоды по комнате И количеству гостей
    existing_periods = db.query(PricePeriod).filter(
        PricePeriod.room_id == room_id,
        PricePeriod.number_of_guests == period_data.number_of_guests  # Добавлен фильтр
    ).all()

    new_start = period_data.start_date
    new_end = period_data.end_date
    periods_to_delete = []
    periods_to_update = []

    for period in existing_periods:
        # Проверка пересечения только с периодами для одинакового количества гостей
        if (period.start_date <= new_end) and (period.end_date >= new_start):
            # Существующий период полностью перекрывается новым
            if period.start_date >= new_start and period.end_date <= new_end:
                periods_to_delete.append(period.id)
            
            # Новый период начинается внутри существующего
            elif new_start > period.start_date and new_start <= period.end_date:
                if new_end >= period.end_date:
                    period.end_date = new_start - timedelta(days=1)
                    periods_to_update.append(period)
                else:
                    # Разделение периода
                    old_end = period.end_date
                    period.end_date = new_start - timedelta(days=1)
                    new_period = PricePeriod(
                        start_date=new_end + timedelta(days=1),
                        end_date=old_end,
                        price=period.price,
                        room_id=room_id,
                        number_of_guests=period_data.number_of_guests  # Сохраняем количество гостей
                    )
                    periods_to_update.append(period)
                    db.add(new_period)
            
            # Новый период заканчивается внутри существующего
            elif new_end >= period.start_date and new_end < period.end_date:
                period.start_date = new_end + timedelta(days=1)
                periods_to_update.append(period)
            
            # Новый период охватывает начало существующего
            elif new_start <= period.start_date and new_end >= period.start_date:
                period.start_date = new_end + timedelta(days=1)
                periods_to_update.append(period)

    # Удаляем перекрытые периоды
    if periods_to_delete:
        db.query(PricePeriod).filter(
            PricePeriod.id.in_(periods_to_delete)
        ).delete(synchronize_session=False)

    # Обновляем модифицированные периоды
    for period in periods_to_update:
        if period.start_date > period.end_date:
            db.delete(period)
        else:
            db.merge(period)

    # Создаем новый период с учетом количества гостей
    new_period = PricePeriod(
        **period_data.dict(),
        room_id=room_id
    )
    
    db.add(new_period)
    db.commit()
    db.refresh(new_period)
    
    return new_period

# Добавьте в router.py для price-periods

@router.post(
    "/rooms/{room_id}/copy-price-periods-to-next-year",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_superuser)]
)
def copy_price_periods_to_next_year(
    room_id: int,
    db: Session = Depends(get_db)
):

    
    # Проверяем существование комнаты
    room = db.query(Room).get(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    
    # Определяем текущий год
    current_year = datetime.now().year
    
    # Находим только периоды из текущего года
    current_periods = db.query(PricePeriod).filter(
        PricePeriod.room_id == room_id,
        extract('year', PricePeriod.start_date) == current_year
    ).all()
    
    # Если нет периодов в текущем году, возвращаем ошибку
    if not current_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No price periods found for current year"
        )
    
    # Создаем новые периоды на следующий год
    new_periods = []
    for period in current_periods:
        try:
            # Копируем период, сдвигая даты на 1 год вперед
            new_start = period.start_date.replace(year=period.start_date.year + 1)
            new_end = period.end_date.replace(year=period.end_date.year + 1)
            
            # Проверяем корректность новых дат
            if new_start > new_end:
                continue
                
            # Проверяем, не существует ли уже такого периода
            existing_period = db.query(PricePeriod).filter(
                PricePeriod.room_id == room_id,
                PricePeriod.start_date == new_start,
                PricePeriod.end_date == new_end,
                PricePeriod.number_of_guests == period.number_of_guests
            ).first()
            
            if existing_period:
                continue
                
            # Создаем новый период
            new_period = PricePeriod(
                start_date=new_start,
                end_date=new_end,
                price=period.price,
                room_id=room_id,
                number_of_guests=period.number_of_guests
            )
            new_periods.append(new_period)
        except ValueError:
            # Пропускаем невалидные даты (например, 29 февраля)
            continue
    
    if len(new_periods) == 0:
        return {
        "message": "Периоды на следующий год уже перенесены"}
    # Сохраняем новые периоды
    for period in new_periods:
        db.add(period)
    
    db.commit()
    

    return {
        "message": f"Успешно создано {len(new_periods)} ценовых периодов на следующий год",
        "copied_periods": len(new_periods)
    }