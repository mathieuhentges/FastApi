from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/submitApplication")
async def handle_form(name: str = Form(...), description: str = Form(...), file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Invalid file type. Only text file supported")

    try:
        content = await file.read()
        text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to read the file")

    return {
        "name": name,
        "description": description,
        "filename": file.filename,
        "file_content": text
    }