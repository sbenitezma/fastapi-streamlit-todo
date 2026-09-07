"""FastAPI application entry point.

Assembles the app, initializes the database on startup and registers the router
with the endpoints. Run it with ``python -m api.main`` or with
``uvicorn api.main:app --port 8000``.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.database import init_db
from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Task Management API", version="1.0.0", lifespan=lifespan)
app.include_router(router)


@app.get("/", tags=["health"])
def root() -> dict:
    """Quick check that the API is alive."""
    return {"status": "ok", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
