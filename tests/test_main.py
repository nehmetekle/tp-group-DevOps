import pytest
from fastapi import HTTPException

from app.main import (
    app,
    create_task,
    delete_task,
    get_task,
    health,
    list_tasks,
    reset_tasks,
    summarize_tasks,
    TaskCreate,
    TaskUpdate,
    toggle_task,
    update_task,
)


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


def test_update_task_changes_title_and_completion(clean_tasks: None) -> None:
    created_task = create_task(TaskCreate(title="Write tests"))

    updated_task = update_task(
        created_task.id,
        TaskUpdate(title="Write more tests", completed=True),
    )

    assert updated_task.id == created_task.id
    assert updated_task.title == "Write more tests"
    assert updated_task.completed is True


def test_update_missing_task_returns_404(clean_tasks: None) -> None:
    with pytest.raises(HTTPException) as error:
        update_task(999, TaskUpdate(title="Missing"))

    assert error.value.status_code == 404
    assert error.value.detail == "Task not found"


def test_toggle_task_completion(clean_tasks: None) -> None:
    created_task = create_task(TaskCreate(title="Toggle me"))

    toggled_task = toggle_task(created_task.id)

    assert toggled_task.completed is True


def test_summarize_tasks_counts_total_completed_and_pending(
    clean_tasks: None,
) -> None:
    create_task(TaskCreate(title="Done", completed=True))
    create_task(TaskCreate(title="Still open"))

    summary = summarize_tasks()

    assert summary.total == 2
    assert summary.completed == 1
    assert summary.pending == 1


def test_metrics_route_is_registered() -> None:
    paths = [route.path for route in app.routes]

    assert "/metrics" in paths
