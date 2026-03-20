from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, RoomMember, Room, Resource
from ..schemas import ResourceCreate, ResourceUpdate, ResourceResponse, ResourceWithChildren
from auth import get_current_user
from typing import List, Optional

router = APIRouter(prefix="/api/rooms/{room_id}/resources", tags=["资源"])


def verify_room_member(room_id: int, user_id: int, db: Session) -> bool:
    """验证用户是否是房间成员"""
    member = db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == user_id
    ).first()
    return member is not None


def build_resource_tree(resources: List[Resource]) -> List[ResourceWithChildren]:
    """构建资源树形结构"""
    resource_map: dict[int, ResourceWithChildren] = {}
    root_resources: List[ResourceWithChildren] = []
    
    # 先把所有资源转换为ResourceWithChildren对象
    for resource in resources:
        resource_dict = ResourceResponse.model_validate(resource).model_dump()
        resource_dict['children'] = []
        resource_obj = ResourceWithChildren(**resource_dict)
        resource_map[resource.id] = resource_obj
    
    # 建立父子关系
    for resource in resources:
        if resource.parent_id is None:
            # 一级资源
            root_resources.append(resource_map[resource.id])
        elif resource.parent_id in resource_map:
            # 子资源，添加到父级的children中
            parent_obj = resource_map[resource.parent_id]
            parent_obj.children.append(resource_map[resource.id])
    
    return root_resources


@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(
    room_id: int,
    resource: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建资源（可以是容器，也可以是物品）"""
    # 验证房间成员
    if not verify_room_member(room_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不是该房间成员"
        )
    
    # 如果指定了parent_id，验证父资源是否存在且属于同一房间
    if resource.parent_id:
        parent = db.query(Resource).filter(
            Resource.id == resource.parent_id,
            Resource.room_id == room_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父资源不存在或不属于该房间"
            )
        # 父资源必须是容器
        if not parent.is_container:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父资源必须是容器"
            )
    
    # 创建资源
    new_resource = Resource(
        name=resource.name,
        description=resource.description,
        quantity=resource.quantity,
        is_container=resource.is_container,
        room_id=room_id,
        parent_id=resource.parent_id
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    
    return new_resource


@router.get("", response_model=List[ResourceResponse])
def get_resources(
    room_id: int,
    parent_id: Optional[int] = None,
    is_container: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资源列表"""
    # 验证房间成员
    if not verify_room_member(room_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不是该房间成员"
        )
    
    query = db.query(Resource).filter(Resource.room_id == room_id)
    
    # 按parent_id筛选
    if parent_id is not None:
        query = query.filter(Resource.parent_id == parent_id)
    else:
        # 默认只返回一级资源
        query = query.filter(Resource.parent_id.is_(None))
    
    # 按是否容器筛选
    if is_container is not None:
        query = query.filter(Resource.is_container == is_container)
    
    resources = query.order_by(Resource.created_at.desc()).all()
    return resources


@router.get("/tree", response_model=List[ResourceWithChildren])
def get_resource_tree(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取完整的资源树（带层级关系）"""
    # 验证房间成员
    if not verify_room_member(room_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不是该房间成员"
        )
    
    # 获取所有资源
    resources = db.query(Resource).filter(
        Resource.room_id == room_id
    ).order_by(Resource.created_at.asc()).all()
    
    # 构建树形结构
    resource_tree = build_resource_tree(resources)
    
    return resource_tree


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    room_id: int,
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资源详情"""
    # 验证房间成员
    if not verify_room_member(room_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不是该房间成员"
        )
    
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.room_id == room_id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    return resource


@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    room_id: int,
    resource_id: int,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新资源"""
    # 验证房间成员
    if not verify_room_member(room_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不是该房间成员"
        )
    
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.room_id == room_id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    # 更新资源信息
    if resource_data.name is not None:
        resource.name = resource_data.name
    if resource_data.description is not None:
        resource.description = resource_data.description
    if resource_data.quantity is not None:
        resource.quantity = resource_data.quantity
    if resource_data.is_container is not None:
        resource.is_container = resource_data.is_container
    
    db.commit()
    db.refresh(resource)
    
    return resource


@router.delete("/{resource_id}")
def delete_resource(
    room_id: int,
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除资源"""
    # 验证房间成员
    if not verify_room_member(room_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不是该房间成员"
        )
    
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.room_id == room_id
    ).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    # 检查是否有子资源
    child_count = db.query(Resource).filter(Resource.parent_id == resource_id).count()
    if child_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先删除该资源下的所有子资源"
        )
    
    db.delete(resource)
    db.commit()
    
    return {"message": "资源已删除"}


@router.get("/{resource_id}/children", response_model=List[ResourceResponse])
def get_resource_children(
    room_id: int,
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资源的子资源列表"""
    # 验证房间成员
    if not verify_room_member(room_id, current_user.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不是该房间成员"
        )
    
    # 验证父资源存在
    parent = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.room_id == room_id
    ).first()
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    children = db.query(Resource).filter(
        Resource.parent_id == resource_id,
        Resource.room_id == room_id
    ).order_by(Resource.created_at.desc()).all()
    
    return children
