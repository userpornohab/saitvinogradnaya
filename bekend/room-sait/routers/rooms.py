from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Body
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import os
from typing import List
from database.database import get_db
from models.room import Room, RoomPhoto, PricePeriod, Amenity, RoomAmenity, Booking, RoomBedOption, BedOption
from schemas.room import RoomResponse, RoomCreate, RoomPhotoBase, RoomFilter, RoomUpdate
from auth.dependencies import check_superuser

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("/", response_model=RoomResponse, dependencies=[Depends(check_superuser)])
def create_room(room_data: RoomCreate, db: Session = Depends(get_db)):
    db_room = Room(
        title_dop=room_data.title_dop or "",
        title=room_data.title,
        floor=room_data.floor,
        description=room_data.description,
        max_guests=room_data.max_guests,
        number_of_rooms=room_data.number_of_rooms
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)

    for period in room_data.price_periods:
        db_period = PricePeriod(
            start_date=period.start_date,
            end_date=period.end_date,
            price=period.price,
            room_id=db_room.id
        )
        db.add(db_period)

    for amenity_id in room_data.amenities:
        amenity = db.query(Amenity).filter(Amenity.id == amenity_id).first()
        if amenity:
            db.add(RoomAmenity(room_id=db_room.id, amenity_id=amenity_id))
    
    for bed_id in room_data.bed_options:
        if not db.query(BedOption).get(bed_id):
            raise HTTPException(status_code=404, detail=f"Bed option {bed_id} not found")
        db.add(RoomBedOption(room_id=db_room.id, bed_option_id=bed_id))    

    db.commit()
    return db_room

@router.post("/{room_id}/upload-photos", response_model=List[RoomPhotoBase], dependencies=[Depends(check_superuser)])
async def upload_photos(
    room_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")

    
    try:
        uploaded_photos = []
        for file in files:
            if file.content_type not in ["image/jpeg", "image/png"]:
                continue

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            filepath = Path("static/uploads") / filename

            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            photo = RoomPhoto(
                url=f"/static/uploads/{filename}",
                is_main=False,  # Все новые фото по умолчанию не главные
                room_id=room_id
            )
            db.add(photo)
            db.flush()  # Фиксируем изменения чтобы получить ID
            db.refresh(photo)  # Обновляем объект из БД

            uploaded_photos.append(photo)

        db.commit()
        
       
            
        return uploaded_photos

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error uploading photos: {str(e)}")

@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room)\
        .options(
            joinedload(Room.photos),
            joinedload(Room.price_periods),
            joinedload(Room.amenities)
        )\
        .filter(Room.id == room_id)\
        .first()
    
    if not room:
        raise HTTPException(404, "Room not found")
    return room

@router.delete("/{room_id}", response_model=RoomResponse, dependencies=[Depends(check_superuser)])
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")
    
    db.delete(room)
    db.commit()
    return room

@router.get("/", response_model=List[RoomResponse])
def get_all_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()

@router.post("/filter", response_model=List[RoomResponse])
def filter_rooms(filter_data: RoomFilter, db: Session = Depends(get_db)):
    rooms = db.query(Room).filter(Room.max_guests >= filter_data.guests).all()
    available_rooms = []
    last_day = filter_data.check_out_date - timedelta(days=1)

    for room in rooms:
        
        price_periods = db.query(PricePeriod).filter(
            PricePeriod.room_id == room.id,
            PricePeriod.number_of_guests >= filter_data.guests,
            PricePeriod.end_date >= filter_data.check_in_date,
            PricePeriod.start_date <= last_day
        ).all()
        
        # 2. Если нет ни одного подходящего периода - комната не подходит
        if not price_periods:
            continue
        
        overlapping_bookings = db.query(Booking).filter(
            Booking.room_id == room.id,
            Booking.check_in_date < filter_data.check_out_date,
            Booking.check_out_date > filter_data.check_in_date
        ).count()
        
        if overlapping_bookings < room.number_of_rooms:
            available_rooms.append(room)
    
    return available_rooms

@router.put("/{room_id}", response_model=RoomResponse, dependencies=[Depends(check_superuser)])
def update_room(
    room_id: int,
    update_data: RoomUpdate,  # Новая схема, которую нужно создать
    db: Session = Depends(get_db)
):
    # Получаем комнату и проверяем существование
    db_room = db.query(Room)\
        .options(joinedload(Room.amenities), joinedload(Room.bed_options))\
        .filter(Room.id == room_id)\
        .first()
    
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Обновляем основные поля
    if update_data.title is not None:
        db_room.title = update_data.title
    if update_data.description is not None:
        db_room.description = update_data.description
    if update_data.max_guests is not None:
        db_room.max_guests = update_data.max_guests
    if update_data.number_of_rooms is not None:
        db_room.number_of_rooms = update_data.number_of_rooms
    if update_data.title_dop is not None:
        db_room.title_dop = update_data.title_dop

    # Обновляем связи многие-ко-многим
    if update_data.bed_options is not None:
        # Удаляем старые связи
        db.query(RoomBedOption).filter(RoomBedOption.room_id == room_id).delete()
        # Добавляем новые
        for bed_id in update_data.bed_options:
            if not db.query(BedOption).get(bed_id):
                raise HTTPException(status_code=404, detail=f"Bed option {bed_id} not found")
            db.add(RoomBedOption(room_id=room_id, bed_option_id=bed_id))

    if update_data.amenities is not None:
        # Удаляем старые связи
        db.query(RoomAmenity).filter(RoomAmenity.room_id == room_id).delete()
        # Добавляем новые
        for amenity_id in update_data.amenities:
            if not db.query(Amenity).get(amenity_id):
                raise HTTPException(status_code=404, detail=f"Amenity {amenity_id} not found")
            db.add(RoomAmenity(room_id=room_id, amenity_id=amenity_id))

    if update_data.floor is not None:
        db_room.floor = update_data.floor

    db.commit()
    db.refresh(db_room)
    return db_room

@router.patch("/{room_id}/photos/{photo_id}", dependencies=[Depends(check_superuser)])
def set_main_photo(
    room_id: int,
    photo_id: int,
    is_main: bool = Body(..., embed=True),  # Важно использовать Body
    db: Session = Depends(get_db)
):
    try:
        # Обновляем все фото комнаты, если устанавливаем главное
        if is_main:
            db.query(RoomPhoto).filter(
                RoomPhoto.room_id == room_id
            ).update({RoomPhoto.is_main: False})
        
        # Обновляем конкретное фото
        photo = db.query(RoomPhoto).filter(
            RoomPhoto.id == photo_id,
            RoomPhoto.room_id == room_id
        ).first()
        
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        
        photo.is_main = is_main
        db.commit()
        return {"message": "Photo updated successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{room_id}/photos/{photo_id}", dependencies=[Depends(check_superuser)])
def delete_room_photo(
    room_id: int,
    photo_id: int,
    db: Session = Depends(get_db)
):
    try:
        photo = db.query(RoomPhoto).filter(
            RoomPhoto.id == photo_id,
            RoomPhoto.room_id == room_id
        ).first()
        
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        
        # Удаляем файл с сервера
        if photo.url:
            file_path = os.path.join("static/uploads", os.path.basename(photo.url))
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Удаляем запись из БД
        db.delete(photo)
        db.commit()
        
        return {"message": "Photo deleted successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting photo: {str(e)}"
        )