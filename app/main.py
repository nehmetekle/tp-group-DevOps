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


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    completed: bool | None = None


class Task(TaskCreate):
    id: int


class TaskSummary(BaseModel):
    total: int
    completed: int
    pending: int


tasks: Dict[int, Task] = {}
next_task_id = 1


Instrumentator().instrument(app).expose(app, endpoint="/metrics")


def reset_tasks() -> None:
    global next_task_id

    tasks.clear()
    next_task_id = 1


def find_task(task_id: int) -> Task:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


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


@app.get("/tasks/summary", response_model=TaskSummary)
def summarize_tasks() -> TaskSummary:
    completed_count = sum(1 for task in tasks.values() if task.completed)
    total_count = len(tasks)

    return TaskSummary(
        total=total_count,
        completed=completed_count,
        pending=total_count - completed_count,
    )


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    return find_task(task_id)


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    task = find_task(task_id)

    updated_task = task.model_copy(
        update={
            "title": payload.title if payload.title is not None else task.title,
            "completed": (
                payload.completed
                if payload.completed is not None
                else task.completed
            ),
        }
    )
    tasks[task_id] = updated_task

    return updated_task


@app.patch("/tasks/{task_id}/toggle", response_model=Task)
def toggle_task(task_id: int) -> Task:
    task = find_task(task_id)
    updated_task = task.model_copy(update={"completed": not task.completed})
    tasks[task_id] = updated_task

    return updated_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    find_task(task_id)
    del tasks[task_id]
