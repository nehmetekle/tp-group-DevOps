from typing import Dict, List

from fastapi import FastAPI, HTTPException, status
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field


app = FastAPI(
    title="DevOps Task API",
    description="Small REST API used for a DevOps CI/CD pipeline project.",
    version="0.1.0",
)


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    completed: bool = False


class Task(TaskCreate):
    id: int


tasks: Dict[int, Task] = {}
next_task_id = 1


Instrumentator().instrument(app).expose(app, endpoint="/metrics")


def reset_tasks() -> None:
    global next_task_id

    tasks.clear()
    next_task_id = 1


@app.get("/health", status_code=status.HTTP_200_OK)
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks", response_model=List[Task])
def list_tasks() -> list[Task]:
    return list(tasks.values())


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    global next_task_id

    task = Task(id=next_task_id, **payload.model_dump())
    tasks[task.id] = task
    next_task_id += 1

    return task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    del tasks[task_id]
