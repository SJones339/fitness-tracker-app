from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../../.env")

sql_password = os.getenv("SQL_URL")
print(sql_password)

engine = create_engine(sql_password)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(engine)

Base.metadata.create_all(bind=engine)

print("Database tables have been reset and recreated.")

#use DROP TABLE if exists __ cascade; (replace __ with table name) if
#there exists dependencies (use of foreign keys) with that table


