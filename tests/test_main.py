import pytest
from fastapi import HTTPException

from app.main import app, create_task, delete_task, get_task, health
from app.main import list_tasks, reset_tasks, TaskCreate


@pytest.fixture()
def clean_tasks() -> None:
    reset_tasks()


def test_health_returns_ok() -> None:
    response = health()

    assert response == {"status": "ok"}


def test_create_and_list_tasks(clean_tasks: None) -> None:
    created_task = create_task(
        TaskCreate(title="Prepare CI pipeline", completed=False)
    )
    all_tasks = list_tasks()

    assert created_task.id == 1
    assert created_task.title == "Prepare CI pipeline"
    assert len(all_tasks) == 1


def test_get_missing_task_returns_404(clean_tasks: None) -> None:
    with pytest.raises(HTTPException) as error:
        get_task(999)

    assert error.value.status_code == 404
    assert error.value.detail == "Task not found"


def test_delete_task(clean_tasks: None) -> None:
    created_task = create_task(TaskCreate(title="Delete me"))

    delete_task(created_task.id)

    assert list_tasks() == []


def test_metrics_route_is_registered() -> None:
    paths = [route.path for route in app.routes]

    assert "/metrics" in paths
