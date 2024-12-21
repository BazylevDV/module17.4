from fastapi import APIRouter, Depends, status, HTTPException, Path
from sqlalchemy.orm import Session
from app.backend.db import get_db
from app.models.user import User
from app.routers.schemas import CreateUser, UpdateUser
from slugify import slugify

router = APIRouter()


@router.get('/', status_code=status.HTTP_200_OK)
def all_users(db: Session = Depends(get_db)):
    """
    Возвращает список всех пользователей из БД.
    """
    users = db.query(User).all()
    return users


@router.get('/{user_id}', status_code=status.HTTP_200_OK)
def user_by_id(
    user_id: int = Path(..., description="ID пользователя, которого нужно получить"),
    db: Session = Depends(get_db)
):
    """
    Возвращает пользователя по его ID.
    Если пользователь не найден, выбрасывает исключение 404.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User was not found")
    return user


@router.post('/create', status_code=status.HTTP_201_CREATED)
def create_user(
    user: CreateUser,
    db: Session = Depends(get_db)
):
    """
    Создает нового пользователя в БД.
    Генерирует slug из username и сохраняет пользователя.
    Возвращает статус создания.
    """
    # Генерация slug из username
    slug = slugify(user.username)

    # Проверка на существование пользователя с таким же slug
    existing_user = db.query(User).filter(User.slug == slug).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this username already exists")

    # Создание нового пользователя
    new_user = User(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        age=user.age,
        slug=slug
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update/{user_id}', status_code=status.HTTP_200_OK)
def update_user(
    user_id: int = Path(..., description="ID пользователя, которого нужно обновить"),
    user: UpdateUser = None,
    db: Session = Depends(get_db)
):
    """
    Обновляет данные пользователя по его ID.
    Если пользователь не найден, выбрасывает исключение 404.
    """
    existing_user = db.query(User).filter(User.id == user_id).first()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    # Обновление данных пользователя
    if user.firstname:
        existing_user.firstname = user.firstname
    if user.lastname:
        existing_user.lastname = user.lastname
    if user.age:
        existing_user.age = user.age

    db.commit()
    db.refresh(existing_user)

    return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}


@router.delete('/delete/{user_id}', status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int = Path(..., description="ID пользователя, которого нужно удалить"),
    db: Session = Depends(get_db)
):
    """
    Удаляет пользователя по его ID.
    Если пользователь не найден, выбрасывает исключение 404.
    Все связанные задачи также удаляются благодаря cascade="all, delete-orphan".
    """
    existing_user = db.query(User).filter(User.id == user_id).first()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    # Удаление пользователя
    db.delete(existing_user)
    db.commit()

    return {'status_code': status.HTTP_200_OK, 'transaction': 'User and associated tasks deleted successfully'}