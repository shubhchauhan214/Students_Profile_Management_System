from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from models import Student
from database import get_db
from typing import List, Optional


router = APIRouter()


# Pydantic schemas for Courses (to be embedded in Student)
class Course(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    student_id: int

    class Config:
        orm_mode = True


# Pydantic schemas for Students
class StudentBase(BaseModel):
    name: str
    email: str
    age: int


class StudentCreate(StudentBase):
    pass


class Student(StudentBase):
    id: int
    courses: List[Course] = []

    class Config:
        orm_mode: True


@router.post("/", response_model=Student, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(name=student.name, email=student.email, age=student.age)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.get("/", response_model=List[Student], status_code=status.HTTP_200_OK)
async def read_students(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=Student, status_code=status.HTTP_200_OK)
async def read_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

