import os
import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import check_db_connection
from app.routers import tags_router, tasks_router, notes_router, user_router, calendar_router, habits_router, profile_router, drawing_router, debrief_router, demo_router

# Comma-separated list of allowed frontend origins, e.g.
# "http://localhost:3000,https://task-master-mvp.vercel.app"
# New deployment targets (a staging URL, a custom domain) are added via env
# var, not a source change.
_DEFAULT_ORIGINS = "http://localhost:3000,https://kanso-web-app.vercel.app"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", _DEFAULT_ORIGINS).split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_url = os.getenv("DATABASE_URL", "")
    masked = db_url[:30] + "..." if len(db_url) > 30 else db_url
    print(f"DATABASE_URL = {masked}")

    if not os.getenv("SUPABASE_JWT_SECRET"):
        warnings.warn(
            "SUPABASE_JWT_SECRET is not set — all authenticated endpoints will return 500. "
            "Add it to .env: Supabase dashboard → Project Settings → API → JWT Secret",
            stacklevel=1,
        )

    try:
        check_db_connection()
    except Exception as exc:
        warnings.warn(f"Startup DB check failed (app will still start): {exc}", stacklevel=1)

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tags_router.router)
app.include_router(tasks_router.router)
app.include_router(notes_router.router)
app.include_router(user_router.router)
app.include_router(calendar_router.router)
app.include_router(habits_router.router)
app.include_router(profile_router.router)
app.include_router(drawing_router.router)
app.include_router(debrief_router.router)
app.include_router(demo_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to TaskMaster Backend"}