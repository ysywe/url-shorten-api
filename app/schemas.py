from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime

class URLBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    url: str = Field(min_length=1, description="URL cannot be empty")

class URLCreate(URLBase):
    pass

class URLUpdate(URLBase):
    pass

class URLResponse(URLBase):
    id: str
    short_code: str = Field(min_length=1, description="Short code cannot be empty", serialization_alias="shortCode")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)

    @field_validator("id", mode="before")
    def convert_int_id_to_str(cls, value):
        return str(value)
    
class URLDetailsResponse(URLResponse):
    access_count: int = Field(default=0, serialization_alias="accessCount")