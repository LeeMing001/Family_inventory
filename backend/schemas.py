from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User相关schemas
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


# Token相关schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Room相关schemas
class RoomBase(BaseModel):
    name: str
    max_members: int = 5


class RoomCreate(RoomBase):
    pass


class RoomJoin(BaseModel):
    code: str


class RoomResponse(RoomBase):
    id: int
    code: str
    owner_id: int
    created_at: datetime
    member_count: int

    class Config:
        from_attributes = True


# RoomMember相关schemas
class RoomMemberResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    joined_at: datetime
    username: str

    class Config:
        from_attributes = True


# Resource相关schemas（统一管理分区和物品）
class ResourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: Optional[int] = None  # 物品才有数量
    is_container: bool = False  # 是否可以作为容器
    parent_id: Optional[int] = None  # 父级资源ID


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    is_container: Optional[bool] = None


class ResourceResponse(ResourceBase):
    id: int
    room_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 带子资源的资源响应
class ResourceWithChildren(ResourceResponse):
    children: List['ResourceWithChildren'] = []


# 更新前向引用
ResourceWithChildren.model_rebuild()
