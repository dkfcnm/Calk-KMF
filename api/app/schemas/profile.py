from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional, List

class ProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    birth_date: date
    birth_time: Optional[time] = None
    birth_city: Optional[str] = None
    birth_city_lat: Optional[float] = None
    birth_city_lon: Optional[float] = None
    birth_timezone: Optional[str] = None
    notes: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    birth_date: Optional[date] = None
    birth_time: Optional[time] = None
    birth_city: Optional[str] = None
    birth_city_lat: Optional[float] = None
    birth_city_lon: Optional[float] = None
    birth_timezone: Optional[str] = None
    notes: Optional[str] = None

class BirthChartResponse(BaseModel):
    id: int
    profile_id: int
    year_pillar: Optional[str] = None
    month_pillar: Optional[str] = None
    day_pillar: Optional[str] = None
    hour_pillar: Optional[str] = None
    day_master: Optional[str] = None
    day_master_element: Optional[str] = None
    calculated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProfileHistoryItem(BaseModel):
    id: int
    action_type: str
    module: Optional[str] = None
    reference_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ProfileResponse(ProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    birth_chart: Optional[BirthChartResponse] = None

    class Config:
        from_attributes = True

class ProfileListResponse(BaseModel):
    items: List[ProfileResponse]
    total: int
