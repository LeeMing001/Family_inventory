from datetime import datetime, timedelta #用于处理JWT过期时间
from typing import Optional
from jose import JWTError, jwt  #Jose是JWT编解码库，用于生成和验证令牌
from passlib.context import CryptContext #passlib提供密码哈希功能，CrptContext统一管理多种哈希算法
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer  #fastapi提供请求管理
from sqlalchemy.orm import Session #session类型提示
from database import get_db   #数据库会话生成器
from models import User  #User用户模型
from datetime import timezone
import config
# 密码加密配置
# 使用 bcrypt_sha256 以避免 bcrypt 的 72 字节限制导致长密码报错
# 普通的bcrypt会超长截取
# bcrypt_sha256先用sha256加密，再使用bcrypt
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

# JWT配置
SECRET_KEY = config.secret_key  # 生产环境应该从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# 创建OAuth2密码方案，告诉FastAPI如何获取密码
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# 密码验证，将明文密码鱼哈希米吗进行对比，返回布尔值
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

# 密码哈希，对明文米吗进行哈希，返回哈希字符串
def get_password_hash(password: str) -> str:
    """密码加密"""
    return pwd_context.hash(password)

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        # expire = datetime.utcnow() + expires_delta # utcnow方法已废弃
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # expire = datetime.utcnow() + timedelta(minutes=20)
        expire = datetime.now(timezone.utc) + timedelta(minutes=20)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def generate_room_code(length: int = 6) -> str:
    """生成房间邀请码"""
    import random
    import string
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
