from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from slugify import slugify
from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session

from app.backend.db_depends import get_db
from app.models.user import User  # Импортируем модель User
from app.models.task import Task  # Импортируем модель Task
from app.routers.schemas import CreateUser, UpdateUser

# Создаем экземпляр APIRouter
router = APIRouter()

# Функция для получения всех пользователей
@router.get("/", status_code=status.HTTP_200_OK)
def all_users(db: Annotated[Session, Depends(get_db)]):
    """
    Возвращает список всех пользователей из БД.
    """
    query = select(User)
    users = db.scalars(query).all()
    return users

# Функция для получения пользователя по ID
@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    Возвращает пользователя по его ID.
    Если пользователь не найден, выбрасывает исключение 404.
    """
    query = select(User).where(User.id == user_id)
    user = db.scalar(query)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    return user

# Функция для создания нового пользователя
@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    """
    Создает нового пользователя в БД.
    Возвращает статус 201 и сообщение об успешной транзакции.
    """
    # Генерируем slug на основе имени пользователя
    user_slug = slugify(user.username)

    # Проверяем, существует ли пользователь с таким username или slug
    existing_user = db.scalar(select(User).where(User.username == user.username))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exists")

    # Создаем новую запись в БД
    query = insert(User).values(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        age=user.age,
        slug=user_slug
    )
    db.execute(query)
    db.commit()

    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}

# Функция для обновления пользователя
@router.put("/update/{user_id}", status_code=status.HTTP_200_OK)
def update_user(user_id: int, user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    """
    Обновляет данные пользователя по его ID.
    Если пользователь не найден, выбрасывает исключение 404.
    """
    # Проверяем, существует ли пользователь с указанным ID
    existing_user = db.scalar(select(User).where(User.id == user_id))
    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    # Генерируем новый slug, если указан username
    if user.username:
        user_slug = slugify(user.username)
    else:
        user_slug = existing_user.slug

    # Обновляем данные пользователя
    query = (
        update(User)
        .where(User.id == user_id)
        .values(
            username=user.username,
            firstname=user.firstname,
            lastname=user.lastname,
            age=user.age,
            slug=user_slug
        )
    )
    db.execute(query)
    db.commit()

    return {"status_code": status.HTTP_200_OK, "transaction": "User update is successful!"}

# Функция для удаления пользователя
@router.delete("/delete/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """
    Удаляет пользователя по его ID.
    Если пользователь не найден, выбрасывает исключение 404.
    """
    # Проверяем, существует ли пользователь с указанным ID
    existing_user = db.scalar(select(User).where(User.id == user_id))
    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    # Удаляем пользователя
    query = delete(User).where(User.id == user_id)
    db.execute(query)
    db.commit()

    return {"status_code": status.HTTP_200_OK, "transaction": "User deleted successfully"}
