from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from models import Student
from database import get_db
from typing import List, Optional


router = APIRouter()


# Pydantic schemas for Courses
class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None


class CourseCreate(CourseBase):
    student_id: int


class Course(CourseBase):
    id: int
    student_id: int

    class Config:
        orm_mode: True




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


@router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    db_course = models.Course(name=course.name, description=course.description, student_id=course.student_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.get("/", response_model=List[Course], status_code=status.HTTP_200_OK)
async def read_courses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    courses = db.query(models.Course).offset(skip).limit(limit).all()
    return courses


@router.get("/{course_id}", response_model=Course, status_code=status.HTTP_200_OK)
async def read_course_by_id(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

