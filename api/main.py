"""FastAPI application entry point.

Assembles the app, initializes the database on startup, registers the router with
the endpoints and maps the service's domain errors onto HTTP responses. Run it
with ``python -m api.main`` or ``uvicorn api.main:app --port 8000``.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.database import Database, default_db_path
from api.routes import router
from api.todos_service import EmptyUpdate, TodoNotFound


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database(default_db_path())
    db.init_schema()
    app.state.db = db
    try:
        yield
    finally:
        db.close()


app = FastAPI(title="Task Management API", version="1.0.0", lifespan=lifespan)
app.include_router(router)


@app.exception_handler(TodoNotFound)
async def _handle_todo_not_found(request: Request, exc: TodoNotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(EmptyUpdate)
async def _handle_empty_update(request: Request, exc: EmptyUpdate) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/", tags=["health"])
def root() -> dict:
    """Quick check that the API is alive."""
    return {"status": "ok", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
