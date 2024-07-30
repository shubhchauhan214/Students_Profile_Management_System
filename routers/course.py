from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from database import get_db
from typing import List, Optional


router = APIRouter()


# Pydantic schemas for Courses
class CourseBase(BaseModel):
    name: str = Field(..., example="Math 101")
    description: Optional[str] = Field(None, example="Basic Math Course")


class CourseCreate(CourseBase):
    student_id: int


class CourseResponse(CourseBase):
    id: int
    student_id: int

    class Config:
        from_attributes: True


# Pydantic schemas for Students
class StudentBase(BaseModel):
    name: str = Field(..., example="shubham Chauhan")
    email: str = Field(..., example="shubham.chauhan@example.com")
    age: int = Field(..., example=0)


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: int
    courses: List[CourseResponse] = []

    class Config:
        from_attributes: True


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    db_course = models.Course(name=course.name, description=course.description, student_id=course.student_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.get("/", response_model=List[CourseResponse], status_code=status.HTTP_200_OK)
async def read_courses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    courses = db.query(models.Course).offset(skip).limit(limit).all()
    return courses


@router.get("/{course_id}", response_model=CourseResponse, status_code=status.HTTP_200_OK)
async def read_course_by_id(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

