from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import models
from database import get_db
from typing import List, Optional

router = APIRouter()


class CourseBase(BaseModel):
    name: str = Field(..., example="Math 101")
    description: Optional[str] = Field(None, example="Basic Math Course")

    class Config:
        from_attributes = True


class CourseResponse(CourseBase):
    id: int

    class Config:
        from_attributes = True


class StudentBase(BaseModel):
    name: str = Field(..., example="shubham Chauhan")
    email: str = Field(..., example="shubham.chauhan@example.com")
    age: int = Field(..., example=0)


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: int
    courses: List[CourseBase] = []

    class Config:
        from_attributes = True


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(name=student.name, email=student.email, age=student.age)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.get("/", response_model=List[StudentResponse], status_code=status.HTTP_200_OK)
async def read_students(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
async def read_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
