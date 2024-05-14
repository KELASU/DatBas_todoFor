# FastAPI
from fastapi import FastAPI, HTTPException, Depends, Request, Response, status, __version__
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Annotated
import crud, models, schemas
from BasicVerifier import BasicVerifier
from database import engine, SessionLocal
from sqlalchemy.orm import Session  
from schemas import Task, User, SessionData
from uuid import UUID, uuid4
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
import uvicorn
from os import getenv
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(bind = engine)

origins = [
    "http://0.0.0.0:5173",
    "http://0.0.0.0"
]

cookie_params = CookieParameters()

cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

backend = InMemoryBackend[UUID, SessionData]()

verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=False,
    backend=backend,
    auth_http_exception=HTTPException(status_code=404, detail="invalid session"),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI on Vercel</title>
        <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
    </head>
    <body>
        <div class="bg-gray-200 p-4 rounded-lg shadow-lg">
            <h1>Hello from FastAPI@{__version__}</h1>
            <ul>
                <li><a href="/docs">/docs</a></li>
                <li><a href="/redoc">/redoc</a></li>
            </ul>
            <p>Powered by <a href="https://vercel.com" target="_blank">Vercel</a></p>
        </div>
    </body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(html)

task_id_count = 0
tasks = {}

user_count = 0
users = {}

@app.post("/createTask")
def create_task(task: Task, db: Session = Depends(get_db)):
    return crud.create_task(db, task)

@app.get("/getTaskID/{id}")
def get_task_by_id(id: int, db: Session = Depends(get_db)):
    return crud.get_task_by_id(db, id)

@app.get("/getTaskTitle/{title}")
def get_task_by_title(title: str, db: Session = Depends(get_db)):

    filtered_tasks = crud.get_task_by_title(db, title)
    if filtered_tasks:
        return filtered_tasks
    else:
        return {"error": f"No tasks found with title '{title}'"}

@app.delete("/deleteTaskID/{id}")
def delete_task_by_id(id: int, db: Session = Depends(get_db)):
    
    return crud.delete_task_by_id(db, id)

@app.delete("/deleteTaskTitle/{title}")
def delete_task_by_title(title: str, db: Session = Depends(get_db)):
    return crud.delete_task_by_title(db, title)

@app.delete("/deleteUser/{email}")
def delete_user_by_email(email: str, db: Session = Depends(get_db)):
    return crud.delete_user_by_email(db, email)

@app.delete("/deleteAll")
def delete_all_tasks(db: Session = Depends(get_db)):
    return crud.delete_all_tasks(db)

@app.delete("/deleteAllUser")
def delete_all_tasks(db: Session = Depends(get_db)):
    return crud.delete_all_users(db)

@app.get("/getAllTasks")
def get_all_tasks(db: Session = Depends(get_db)):

    return crud.get_tasks(db)

@app.put("/updateTask/{id}")
def update_task(id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    updated_task = crud.update_task(db, id, task_update)
    return updated_task

@app.put("/updateCompletion/{id}")
def update_completion_task_by_id(id: int, task_update_completion: schemas.TaskUpdateCompletion, db: Session = Depends(get_db)):
    updated_task = crud.update_completion_task(db, id, task_update_completion)
    return updated_task

## User
@app.post("/createUser")
def create_user(user: User, db: Session = Depends(get_db)):
    # db_user =  crud.get_user_by_email(db, user.email)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/getUserID/{user_id}")    
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_by_id(db, user_id)

@app.get("/getUserEmail/{user_email}")    
def get_user_by_id(user_email: str, db: Session = Depends(get_db)):
    return crud.get_user_by_email(db, user_email)

@app.get("/verifyUser")
def verify_user(email: str, password: str, db: Session = Depends(get_db)):
    return crud.verify_user(db, email, password)
    
## Sessions
@app.post("/create_session/{user_id}")
async def create_session(user_id: int, response: Response, db: Session = Depends(get_db)):
    session = uuid4()
    data = SessionData(user_id=user_id)

    await backend.create(session, data)
    cookie.attach_to_response(response, session) 
    crud.create_session(db, session, user_id)

    return f"created session for {user_id}"


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data


@app.delete("/delete_session", dependencies=[Depends(cookie)])
async def del_session(response: Response, session_id: UUID = Depends(cookie), db: Session = Depends(get_db)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    crud.delete_session(db)

    return "deleted session"

if __name__ == '__main__':
    uvicorn.run("main:app", host = "0.0.0.0", reload=True)