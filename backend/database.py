from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 数据库文件路径
DATABASE_URL = "sqlite:///./family_inventory.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 导入Base用于创建表（从models导入）
Base = None  # 将在导入models后被设置

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    # 导入模型，确保表能被创建
    from models import Base as ModelBase, User, Room, RoomMember, Resource
    global Base
    Base = ModelBase
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成")
