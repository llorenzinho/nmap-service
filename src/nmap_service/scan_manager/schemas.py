from datetime import datetime

from pydantic import BaseModel

from nmap_service.core.enums import TaskStatus


class SubmitJobSchema(BaseModel):
    target: str
    ports: list[str] | None = None


class CreateJobSchema(SubmitJobSchema):
    extra_flags: str | None = None
    command: str


class SummaryResponse(BaseModel):
    num_ports: int
    elapsed_seconds: float | None = None
    target: str


class ErrorSummaryResponse(BaseModel):
    message: str


class JobStatusResponse(BaseModel):
    status: TaskStatus
    summary: SummaryResponse | ErrorSummaryResponse | None = None


class JobStatusListResponse(BaseModel):
    id: str | int
    timestamp: datetime | None = None
    status: TaskStatus
