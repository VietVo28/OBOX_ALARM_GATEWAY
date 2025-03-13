from fastapi import HTTPException
from typing import Annotated, Union
from datetime import datetime, timedelta, timezone
import jwt
from tortoise.expressions import Q

from app.core.setting_env import settings
from app.dto.user_dto import UserRegisterDTO, UserUpdateDTO
from passlib.context import CryptContext

from app.models.user import User


class UserService:
    async def register_user(self, user: UserRegisterDTO):
        user_exists = await User.filter(username=user.username).first()
        if user_exists:
            raise HTTPException(status_code=400, detail="Username đã tồn tại")

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(user.password)

        user = await User.create(username=user.username, password=hashed_password)
        return user.username

    async def update_user(self, user: UserUpdateDTO, id: str):
        try:
            user_exists = await User.get(id=id)
        except:
            raise HTTPException(status_code=404, detail="User không tồn tại")
        if not user_exists:
            raise HTTPException(status_code=404, detail="User không tồn tại")

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        if user.password:
            hashed_password = pwd_context.hash(user.password)
            await User.filter(id=id).update(password=hashed_password)
        if user.username:
            await User.filter(id=id).update(username=user.username)
        return user.username

    async def create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def login(self, user: UserRegisterDTO):
        username = user.username
        password = user.password
        user = await User.filter(username=username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User không tồn tại")

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        if not pwd_context.verify(password, user.password):
            raise HTTPException(status_code=400, detail="Sai mật khẩu")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await self.create_access_token(data={"sub": user.username, "id_user": str(user.id)},
                                                      expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_all(self, page: int, size: int, key_work=None):
        query = Q()
        if key_work:
            query = Q(username__icontains=key_work)

        data = await User.filter(query).offset(page * size).limit(size).order_by("-created_at")
        data_resuilt = []
        for item in data:
            data_resuilt.append({
                "id": item.id,
                "username": item.username,
                "created_at": item.created_at,
                "updated_at": item.updated_at
            })
        total = await User.filter(query).count()
        return {
            "total": total,
            "data": data_resuilt
        }

    async def delete_user(self, id: str, current_user: User):
        try:
            user = await User.get(id=id)
        except:
            raise HTTPException(status_code=404, detail="User không tồn tại")
        if not user:
            raise HTTPException(status_code=404, detail="User không tồn tại")
        if str(user.id) == str(current_user.id):
            raise HTTPException(status_code=400, detail="Không thể xóa chính mình")
        total = await User.all().count()
        if total == 1:
            raise HTTPException(status_code=400, detail="Không thể xóa user cuối cùng")
        await User.filter(id=id).delete()
        return "Xóa thành công"


user_service = UserService()
