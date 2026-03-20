from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Room, RoomMember
from schemas import RoomCreate, RoomResponse, RoomJoin, RoomMemberResponse
from auth import get_current_user, generate_room_code
from typing import List

router = APIRouter(prefix="/api/rooms", tags=["房间"])


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建房间"""
    # 生成唯一的房间码
    code = generate_room_code()
    while db.query(Room).filter(Room.code == code).first():
        code = generate_room_code()
    
    new_room = Room(
        name=room.name,
        owner_id=current_user.id,
        code=code,
        max_members=room.max_members
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    
    # 房主自动加入房间
    room_member = RoomMember(
        room_id=new_room.id,
        user_id=current_user.id
    )
    db.add(room_member)
    db.commit()
    
    # 添加成员数量
    new_room.member_count = 1
    return new_room


@router.post("/join")
def join_room(
    room_join: RoomJoin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """通过邀请码加入房间"""
    # 查找房间
    room = db.query(Room).filter(Room.code == room_join.code).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="房间不存在或邀请码错误"
        )
    
    # 检查是否已是成员
    existing_member = db.query(RoomMember).filter(
        RoomMember.room_id == room.id,
        RoomMember.user_id == current_user.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="你已经是该房间成员"
        )
    
    # 检查房间是否已满
    member_count = db.query(RoomMember).filter(RoomMember.room_id == room.id).count()
    if member_count >= room.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="房间已满"
        )
    
    # 加入房间
    room_member = RoomMember(
        room_id=room.id,
        user_id=current_user.id
    )
    db.add(room_member)
    db.commit()
    
    return {"message": "成功加入房间"}


@router.get("", response_model=List[RoomResponse])
def get_my_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有房间"""
    rooms = db.query(Room).join(RoomMember).filter(
        RoomMember.user_id == current_user.id
    ).all()
    
    # 添加成员数量
    for room in rooms:
        room.member_count = db.query(RoomMember).filter(
            RoomMember.room_id == room.id
        ).count()
    
    return rooms


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取房间详情"""
    # 检查是否是房间成员
    member = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不是该房间成员"
        )
    
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="房间不存在"
        )
    
    # 添加成员数量
    room.member_count = db.query(RoomMember).filter(
        RoomMember.room_id == room.id
    ).count()
    
    return room


@router.get("/{room_id}/members", response_model=List[RoomMemberResponse])
def get_room_members(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取房间成员列表"""
    # 检查是否是房间成员
    member = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不是该房间成员"
        )
    
    members = db.query(RoomMember, User).join(User).filter(
        RoomMember.room_id == room_id
    ).all()
    
    result = []
    for rm, user in members:
        result.append(RoomMemberResponse(
            id=rm.id,
            user_id=rm.user_id,
            room_id=rm.room_id,
            joined_at=rm.joined_at,
            username=user.username
        ))
    
    return result
