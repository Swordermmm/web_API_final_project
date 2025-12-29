from fastapi import APIRouter
from app.tasks.task import background_task
from app.models.schemas import TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/run", response_model=TaskResponse)
async def run_background_task():
    await background_task.run_once()
    return TaskResponse(
        message="Background task executed manually",
        task_id="manual_execution"
    )