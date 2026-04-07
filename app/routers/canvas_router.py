from fastapi import APIRouter, HTTPException
from httpx import HTTPStatusError

from app.database.canvas_db import get_canvas

router = APIRouter(
    prefix="/canvas",
    tags=["Canvas"],
)

@router.get("/user-profile")
async def get_user_profile():
    try:
        return await get_canvas("/users/self/profile")
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )

@router.get("/user-courses")
async def get_user_courses():
    try:
        return await get_canvas("/courses?enrollment_state=active")
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )

@router.get("/courses/{course_id}/modules")
async def get_course_modules(course_id: int):
    try:
        return await get_canvas(
            f"/courses/{course_id}/modules",
            params={"per_page": 100},
        )
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )

@router.get("/courses/{course_id}/assignments")
async def get_course_assignments(course_id: int):
    try:
        return await get_canvas(
            f"/courses/{course_id}/assignments",
            params={"per_page": 100},
        )
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )

@router.get("/courses/{course_id}/quizzes")
async def get_course_quizzes(course_id: int):
    try:
        return await get_canvas(
            f"/courses/{course_id}/quizzes",
            params={"per_page": 100},
        )
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )

@router.get("/courses/{course_id}/modules/{module_id}/items")
async def get_course_module_items(course_id: int, module_id: int):
    try:
        return await get_canvas(
            f"/courses/{course_id}/modules/{module_id}/items",
            params={"per_page": 100},
        )
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )

@router.get("/courses/{course_id}/assignments/{assignment_id}")
async def get_course_assignment_item(course_id: int, assignment_id: int):
    try:
        return await get_canvas(
            f"/courses/{course_id}/assignments/{assignment_id}",
            params={"per_page": 100},
        )
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )

@router.get("/courses/{course_id}/quizzes/{quiz_id}")
async def get_course_quizzes(course_id: int, quiz_id: int):
    try:
        return await get_canvas(
            f"/courses/{course_id}/quizzes/{quiz_id}",
            params={"per_page": 100},
        )
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )
                  