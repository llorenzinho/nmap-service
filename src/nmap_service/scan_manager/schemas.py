from datetime import datetime, timedelta

from pydantic import BaseModel

from nmap_service.core.enums import TaskStatus


class SubmitJobSchema(BaseModel):
    target: str
    ports: list[str] | None = None


class CreateJobSchema(SubmitJobSchema):
    extra_flags: str | None = None


class SummaryResponse(BaseModel):
    num_ports: int
    elapsed_time: timedelta | None = None
    ports: list[str]
    target: str


class JobStatusResponse(BaseModel):
    status: TaskStatus
    summary: SummaryResponse | None = None


class JobStatusListResponse(BaseModel):
    id: str | int
    timestamp: datetime | None = None
    status: TaskStatus
