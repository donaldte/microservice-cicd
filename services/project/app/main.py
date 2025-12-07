from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Project Service")
Instrumentator().instrument(app).expose(app)  

class Task(BaseModel):
    id: int
    title: str
    done: bool = False


fake_tasks_db: List[Task] = [
    Task(id=1, title="Créer la structure du projet", done=True),
    Task(id=2, title="Écrire les services FastAPI", done=False),
    Task(id=3, title="Écrire les tests unitaires", done=False),
]


@app.get("/health")
def health():
    return {"status": "ok", "service": "project"}


@app.get("/tasks")
def list_tasks():
    return fake_tasks_db


@app.post("/tasks")
def create_task(task: Dict):
    id = task['id']
    title = task['title']
    done = task['done']
    task = Task(id=id, title=title, done=done)
    fake_tasks_db.append(task)
    return {"message": "task created (fake)", "task": task}

