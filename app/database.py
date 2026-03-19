# from typing import Annotated

# from fastapi import Depends, FastAPI, HTTPException, Query
# from sqlmodel import Field, Session, SQLModel, create_engine, select

# DATABASE_URL = 'postgresql://postgres:sachi@localhost/fastapi'
# # connect_args = {"check_same_thread": False} # this for sqllite because SQLite doesn't allow the same connection to be used across multiple threads by default.
# # engine = create_engine(DATABASE_URL,connect_args=connect_args)
# engine = create_engine(DATABASE_URL,pool_size=10,max_overflow=20)

# def get_session():
#     with Session(engine,autocommit=False, autoflush=False) as session: # autocommit=False, autoflush=False by default false
#         yield session
# # SessionDep = Annotated[Session, Depends(get_session)]

from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel

import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)

Base = declarative_base()  # replaces SQLModel

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

