from fastapi import FastAPI
from app.routers import tags_router, tasks_router, canvas_router, notes_router, calendar_settings_router, user_router, google_calendar_router
from app.routers import work_blocks_router
from app.routers import availability_preference_router
# Import models so Alembic's autogenerate and SQLAlchemy's metadata pick them up.
import app.models.work_block_model              # noqa: F401
import app.models.availability_preference_model  # noqa: F401
from app.database.database import check_db_connection
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://task-master-mvp.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    db_url = os.getenv("DATABASE_URL", "")
    masked = db_url[:30] + "..." if len(db_url) > 30 else db_url
    print(f"DATABASE_URL = {masked}")

    if not os.getenv("SUPABASE_JWT_SECRET"):
        import warnings
        warnings.warn(
            "SUPABASE_JWT_SECRET is not set — all authenticated endpoints will return 500. "
            "Add it to .env: Supabase dashboard → Project Settings → API → JWT Secret",
            stacklevel=1,
        )

    check_db_connection()

app.include_router(tags_router.router)
app.include_router(tasks_router.router)
app.include_router(canvas_router.router)
app.include_router(notes_router.router)
app.include_router(calendar_settings_router.router)
app.include_router(user_router.router)
app.include_router(google_calendar_router.router)
app.include_router(work_blocks_router.router)
app.include_router(availability_preference_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to TaskMaster Backend"}