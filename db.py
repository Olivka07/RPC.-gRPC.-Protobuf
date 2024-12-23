from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./terms.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TermModel(Base):
    __tablename__ = "terms"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, unique=True, index=True)
    definition = Column(String)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()