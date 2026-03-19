from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 关系
    owned_rooms = relationship("Room", back_populates="owner")
    room_memberships = relationship("RoomMember", back_populates="user")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(10), unique=True, index=True, nullable=False)  # 房间邀请码
    created_at = Column(DateTime, default=datetime.utcnow)
    max_members = Column(Integer, default=5)

    # 关系
    owner = relationship("User", back_populates="owned_rooms")
    members = relationship("RoomMember", back_populates="room")
    resources = relationship("Resource", back_populates="room", cascade="all, delete-orphan")


class RoomMember(Base):
    __tablename__ = "room_members"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    room = relationship("Room", back_populates="members")
    user = relationship("User", back_populates="room_memberships")

    # 确保一个用户在同一房间中只存在一次
    __table_args__ = (UniqueConstraint('room_id', 'user_id', name='_room_user_uc'),)


class Resource(Base):
    """
    统一的资源表，可以既是容器（分区）又是物品
    例如：
    - "厨房"：name="厨房", is_container=True, parent_id=None, quantity=None
    - "冰箱"：name="冰箱", is_container=True, parent_id=厨房.id, description="海尔双开门冰箱"
    - "大米"：name="大米", is_container=False, parent_id=冰箱.id, quantity=10
    """
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)  # 物品描述（容器也可以有）
    quantity = Column(Integer, nullable=True)  # 数量，物品才有，容器可以为null
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("resources.id"), nullable=True)  # 父级资源
    is_container = Column(Boolean, default=False)  # 是否可以作为容器
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    room = relationship("Room", back_populates="resources")
    parent = relationship("Resource", remote_side=[id], backref="children")
