from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStepResult(BaseModel):
    step: str
    system: str
    status: str
    output: dict[str, Any] = Field(default_factory=dict)
    duration_ms: float = 0.0


class WorkflowResult(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    steps: list[WorkflowStepResult] = Field(default_factory=list)
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None
    governance: dict[str, Any] = Field(default_factory=dict)
    final_output: dict[str, Any] = Field(default_factory=dict)
