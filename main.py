from datetime import datetime
from fastapi import FastAPI

from routers import schools, students, invoices
from infrastructure.database.db_engine import engine, Base
from fastapi_pagination import add_pagination


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(schools.router)
app.include_router(students.router)
app.include_router(invoices.router)

add_pagination(app)


@app.get("/")
async def read_root():
    return {
        "status": "ok",
        "message": "System is running",
        "service": "mattilda-test-api",
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
