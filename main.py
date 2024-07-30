from fastapi import FastAPI
from database import engine, Base
from routers import student, course

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(student.router, prefix="/students", tags=["students"])
app.include_router(course.router, prefix="/courses", tags=["courses"])