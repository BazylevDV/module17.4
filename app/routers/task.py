from fastapi import APIRouter, Depends, status, HTTPException, Path, Body
from sqlalchemy.orm import Session
from slugify import slugify
from app.backend.db import get_db
from app.models.user import User
from app.models.task import Task
from app.routers.schemas import CreateTask, UpdateTask

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def all_tasks(db: Session = Depends(get_db)):
    """
    Возвращает список всех задач из БД.
    """
    tasks = db.query(Task).all()
    return tasks


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
def task_by_id(
    task_id: int = Path(..., description="ID задачи, которую нужно получить"),
    db: Session = Depends(get_db)
):
    """
    Возвращает задачу по её ID.
    Если задача не найдена, выбрасывает исключение 404.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task was not found")
    return task


@router.post("/create/{user_id}", status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: int = Path(..., description="ID пользователя, для которого создается задача"),
    task: CreateTask = Body(...),  # Указываем, что task — это тело запроса
    db: Session = Depends(get_db)
):
    """
    Создает новую задачу в БД.
    Принимает модель CreateTask и user_id.
    Подставляет в таблицу Task запись значениями указанными в CreateTask и user_id, если пользователь найден.
    Возвращает словарь {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}.
    В случае отсутствия пользователя выбрасывает исключение с кодом 404 и описанием "User was not found".
    """
    # Проверяем, существует ли пользователь с указанным ID
    existing_user = db.query(User).filter(User.id == user_id).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    # Генерируем slug для задачи
    slug = slugify(task.title)

    # Создаем новую задачу
    new_task = Task(
        title=task.title,
        content=task.content,
        priority=task.priority,
        completed=task.completed,  # Убедитесь, что поле completed передается
        user_id=user_id,
        slug=slug
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put("/update/{task_id}", status_code=status.HTTP_200_OK)
def update_task(
    task_id: int = Path(..., description="ID задачи, которую нужно обновить"),
    task: UpdateTask = Body(...),  # Указываем, что task — это тело запроса
    db: Session = Depends(get_db)
):
    """
    Обновляет данные задачи по её ID.
    Если задача не найдена, выбрасывает исключение 404.
    """
    existing_task = db.query(Task).filter(Task.id == task_id).first()
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task was not found")

    # Обновляем данные задачи
    if task.title:
        existing_task.title = task.title
    if task.content:
        existing_task.content = task.content
    if task.priority:
        existing_task.priority = task.priority
    if task.completed is not None:
        existing_task.completed = task.completed

    db.commit()
    db.refresh(existing_task)

    return {"status_code": status.HTTP_200_OK, "transaction": "Task update is successful!"}


@router.delete("/delete/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int = Path(..., description="ID задачи, которую нужно удалить"),
    db: Session = Depends(get_db)
):
    """
    Удаляет задачу по её ID.
    Если задача не найдена, выбрасывает исключение 404.
    """
    existing_task = db.query(Task).filter(Task.id == task_id).first()
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task was not found")

    # Удаляем задачу
    db.delete(existing_task)
    db.commit()

    return {"status_code": status.HTTP_200_OK, "transaction": "Task deleted successfully"}