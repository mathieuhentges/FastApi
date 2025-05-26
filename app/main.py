from fastapi import Depends, FastAPI, Form, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from aiocache import cached, caches

from app.db import get_async_session
from app.models import Application
from app.osv import get_dependency_vulnerability

app = FastAPI()

caches.set_config({
    "default": {
        "cache": "aiocache.RedisCache",
        "endpoint": "redis",        # This matches your docker service name
        "port": 6379,
        "timeout": 1,
        "serializer": {
            "class": "aiocache.serializers.JsonSerializer"
        }
    }
})

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@cached(ttl=43200)
@app.get("/applications", response_class=HTMLResponse)
async def getApplications(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Application).where(Application.user_id == 1))
    apps = result.scalars().all()

    if not apps:
        raise HTTPException(status_code=404, detail="No applications found for this user.")
    return JSONResponse(content=[app.serialize() for app in apps])


@cached(ttl=43200)
@app.get("/dependencies", response_class=HTMLResponse)
async def get_dependencies(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Application).where(Application.user_id == 1))
    apps = result.scalars().all()
    dependencies = []
    vulnerabilities = []
    if not apps:
        raise HTTPException(status_code=404, detail="No applications found for this user.")
    for app in apps:
        dependencies = list(set(dependencies + app.get_dependencies()))
    for dependency in dependencies:
        vulnerabilities.append(get_dependency_vulnerability(dependency))
    return JSONResponse({"dependencies": dependencies, "vulnerabilities": vulnerabilities})


@cached(ttl=43200)
@app.get("/dependency/{dependency_name}")
async def get_dependency(dependency_name: str, session: AsyncSession = Depends(get_async_session)):
    used_in = []
    result = await session.execute(select(Application).where(Application.user_id == 1))
    apps = result.scalars().all()
    for app in apps:
        if dependency_name in app.get_dependencies():
            used_in.append(app.title)
    return JSONResponse({
        "dependency": dependency_name,
        "vulnerabilities": get_dependency_vulnerability(dependency_name),
        "applications": used_in
    })


@app.post("/submitApplication")
async def handle_form(name: str = Form(...),
                      description: str = Form(...),
                      file: UploadFile = File(...),
                      session: AsyncSession = Depends(get_async_session)
):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Invalid file type. Only text file supported")

    try:
        content = await file.read()
        text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to read the file")
    try:
        new_app = Application(
            user_id=1,  # Will be a table
            title=name,
            description=description,
            requirement=text
        )
        session.add(new_app)
        await session.commit()
        await session.refresh(new_app)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "id": new_app.id,
        "name": name,
        "description": description,
        "filename": file.filename,
        "file_content": text
    }