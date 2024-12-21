from pydantic import BaseModel

# Схема для создания пользователя
class CreateUser(BaseModel):
    username: str
    firstname: str
    lastname: str
    age: int

# Схема для обновления пользователя
class UpdateUser(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    age: int | None = None

# Схема для создания задачи
class CreateTask(BaseModel):
    title: str
    content: str
    priority: int = 0  # Устанавливаем значение по умолчанию
    completed: bool = False  # Добавляем поле completed
    user_id: int  # Добавляем поле user_id

# Схема для обновления задачи
class UpdateTask(BaseModel):
    title: str | None = None  # Делаем поля необязательными
    content: str | None = None
    priority: int | None = None
    completed: bool | None = None  # Добавляем поле completed