from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from .api import teams, players, salary_cap
from .database.init_db import init_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for database initialization"""
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    yield

app = FastAPI(title="NFL GM Simulator", version="1.0.0", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(salary_cap.router, prefix="/api/salary-cap", tags=["salary-cap"])

@app.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/teams", response_class=HTMLResponse)
async def teams_page(request: Request):
    """Teams page"""
    return templates.TemplateResponse("teams.html", {"request": request})

@app.get("/roster", response_class=HTMLResponse)
async def roster_page(request: Request):
    """Roster management page"""
    return templates.TemplateResponse("roster.html", {"request": request})

@app.get("/salary-cap", response_class=HTMLResponse)
async def salary_cap_page(request: Request):
    """Salary cap management page"""
    return templates.TemplateResponse("salary_cap.html", {"request": request})

@app.get("/player/{player_id}", response_class=HTMLResponse)
async def player_detail_page(request: Request, player_id: int):
    """Player detail page"""
    return templates.TemplateResponse("player_detail.html", {"request": request, "player_id": player_id})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
