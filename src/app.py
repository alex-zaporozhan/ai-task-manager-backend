from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from src.infrastructure.database.session import engine
from src.api.routes import router as tasks_router
from src.api.auth_routes import router as auth_router
from src.api.department_routes import router as dept_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    title="Enterprise AI Task Manager",
    version="2.1.0",
    lifespan=lifespan
)

# 1. Подключаем API
app.include_router(auth_router)
app.include_router(dept_router)
app.include_router(tasks_router)

# 2. Подключаем папку со статикой (css, js, html)
# Создай папку src/static руками, если её нет!
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# 3. Главная страница (отдает наш index.html)
@app.get("/")
async def read_index():
    return FileResponse("src/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)