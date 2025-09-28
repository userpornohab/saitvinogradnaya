from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional

class PricePeriodBase(BaseModel):
    number_of_guests: int = Field(gt=0, default=1)
    start_date: date
    end_date: date
    price: int
    

class UserInfo(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True


class PricePeriodCreate(PricePeriodBase):
    pass

class PricePeriodResponse(PricePeriodBase):
    room_id: int
    id: int

    class Config:
        orm_mode = True

class BedOptionBase(BaseModel):
    name: str
    icon: str

class BedOptionCreate(BedOptionBase):
    pass

class BedOptionResponse(BedOptionBase):
    id: int

    class Config:
        orm_mode = True

class RoomPhotoBase(BaseModel):
    url: str
    is_main: bool

class RoomPhotoResponse(RoomPhotoBase):
    id: int
    room_id: int

    class Config:
        orm_mode = True

class AmenityBase(BaseModel):
    id: int  # Добавляем ID в ответ
    name: str
    icon: str

    class Config:
        orm_mode = True  # Включаем парсинг ORM-объектов


class RoomUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    max_guests: Optional[int] = None
    number_of_rooms: Optional[int] = None
    title_dop: Optional[str] = None
    bed_options: Optional[List[int]] = None
    amenities: Optional[List[int]] = None
    floor: Optional[int] = None  # Добавленное поле

class AmenityCreate(AmenityBase):
    pass

class AmenityResponse(AmenityBase):
    id: int

    class Config:
        orm_mode = True

class BookingBase(BaseModel):
    check_in_date: date
    check_out_date: date
    room_id: int


class BookingClientData(BaseModel):
    guest_name: Optional[str] = Field(None, min_length=0, max_length=100)
    guest_phone: Optional[str] = Field(None, min_length=0, max_length=20)
    guest_comment: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = None
    number_of_guests: Optional[int] = 1



class BookingCreate(BookingClientData, BookingBase):

    pass

class BookingUpdate(BookingCreate):

    pass

class BookingResponse(BookingUpdate):
    id: int

    class Config:
        orm_mode = True

class RoomBase(BaseModel):
    id: int
    title: str
    description: str
    max_guests: int
    number_of_rooms: int
    title_dop: str
    floor: Optional[int] = None  # Добавленное поле


class RoomCreate(RoomBase):
    price_periods: List[PricePeriodCreate] = []
    amenities: List[int] = []
    bed_options: List[int] = []

class RoomResponse(RoomBase):
    photos: List[RoomPhotoResponse]
    price_periods: List[PricePeriodResponse]
    amenities: List[AmenityResponse]
    bed_options: List[BedOptionResponse]
    title_dop: Optional[str] = None  # Добавляем сюда
    floor: Optional[int] = None


    class Config:
        orm_mode = True

class RoomFilter(BaseModel):
    guests: int
    check_in_date: date
    check_out_date: date

class CourtyardPhotoBase(BaseModel):
    url: str

class CourtyardPhotoCreate(CourtyardPhotoBase):
    pass

class CourtyardPhotoResponse(CourtyardPhotoBase):
    id: int
    class Config:
        orm_mode = True

class TestimonialBase(BaseModel):
    author_icon_url:Optional[str] = None
    author_name: str
    comment: str

class TestimonialCreate(TestimonialBase):
    pass

class TestimonialResponse(TestimonialBase):
    id: int
    class Config:
        orm_mode = True

class FAQBase(BaseModel):
    question: str
    answer: str

class FAQCreate(FAQBase):
    pass

class FAQResponse(FAQBase):
    id: int
    class Config:
        orm_mode = True

class SiteInfoBase(BaseModel):
    main_photo: Optional[str] = None
    main_description: Optional[str] = None

class SiteInfoResponse(SiteInfoBase):
    courtyard_photos: List[CourtyardPhotoResponse] = []
    testimonials: List[TestimonialResponse] = []
    faqs: List[FAQResponse] = []
    class Config:
        orm_mode = True

class SiteInfoUpdate(SiteInfoBase):
    pass