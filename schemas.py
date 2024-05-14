from typing import Union
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class Task(BaseModel):
    task_id: int
    title: str
    completed: bool = False
    # user_id: Optional[int]

class User(BaseModel):
    id: int
    username: str
    email: str
    password: str

class CreateUser(BaseModel):
    username: str
    email: str
    password: str

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="The updated title of the task")
    completed: Optional[bool] = Field(None, description="The updated completion status of the task")

class TaskUpdateCompletion(BaseModel):
    completed: Optional[bool] = Field(None, description = "Change Completion")

class SessionData(BaseModel):
    user_id: int