from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Создаем движок базы данных
DATABASE_URL = "sqlite:///taskmanager.db"
engine = create_engine(DATABASE_URL, echo=True)

# Создаем локальную сессию
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()